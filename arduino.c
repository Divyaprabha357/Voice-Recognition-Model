#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include "driver/i2s.h"
#include <WiFi.h>
#include <WiFiClient.h>

#define OLED_SDA 8
#define OLED_SCL 9
#define LED_PIN 18

#define BUTTON_TALK 4
#define BUTTON_HELP 5
#define BUTTON_NEXT 6
#define BUTTON_SELECT 7

#define I2S_BCLK 15
#define I2S_WS 16
#define I2S_SD 17

#define I2S_PORT I2S_NUM_0
#define AUDIO_SAMPLES 320
#define AUDIO_BYTES (AUDIO_SAMPLES * 2)

const char* WIFI_SSID = "Divya's Samsung A36";
const char* WIFI_PASSWORD = "12348765";
const char* LAPTOP_IP = "10.117.245.113";
const uint16_t LAPTOP_PORT = 5000;

static const uint8_t MAGIC_1 = 0xAA;
static const uint8_t MAGIC_2 = 0x55;
static const uint8_t PACKET_AUDIO = 0x01;
static const uint8_t PACKET_BUTTON = 0x02;

Adafruit_SH1106G display(128, 64, &Wire, -1);
WiFiClient client;

int32_t rawSamples[AUDIO_SAMPLES];
int16_t pcm[AUDIO_SAMPLES];
uint8_t audioPayload[AUDIO_BYTES];

bool talkEnabled = false;
bool displayReady = false;
bool helpMenuActive = false;
bool appStopped = false;
bool wifiWasConnected = false;

bool lastTalk = HIGH;
bool lastHelp = HIGH;
bool lastNext = HIGH;
bool lastSelect = HIGH;
bool selectLongTriggered = false;

uint32_t debounceTalk = 0;
uint32_t debounceHelp = 0;
uint32_t debounceNext = 0;
uint32_t debounceSelect = 0;
uint32_t selectPressedAt = 0;
uint32_t lastWiFiAttempt = 0;
uint32_t lastServerAttempt = 0;

const uint32_t DEBOUNCE_MS = 45;
const uint32_t EXIT_HOLD_MS = 2000;

const char *helpPages[][6] = {
  {"HELP: COMMANDS 1/4", "VOLUME UP", "VOLUME DOWN",
   "MUTE / UNMUTE", "OPEN NOTEPAD", "OPEN CALCULATOR"},
  {"HELP: COMMANDS 2/4", "OPEN FILE EXPLORER", "OPEN BROWSER",
   "NEXT SLIDE", "PREVIOUS SLIDE", "FIRST / LAST SLIDE"},
  {"HELP: COMMANDS 3/4", "START PRESENTATION", "END PRESENTATION",
   "PLAY / PAUSE", "NEXT TRACK", "PREVIOUS TRACK"},
  {"HELP: COMMANDS 4/4", "GO HOME", "CLOSE TAB",
   "NEW WINDOW", "CLOSE WINDOW", "EXIT VOICE REMOTE"}
};

uint8_t helpPage = 0;

void showStatus(const char *line1, const char *line2 = "") {
  if (!displayReady) return;

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0, 5);
  display.println("VOICE REMOTE");
  display.drawLine(0, 17, 127, 17, SH110X_WHITE);
  display.setCursor(0, 25);
  display.println(line1);
  display.setCursor(0, 40);
  display.println(line2);
  display.display();
}

void showHelpPage() {
  if (!displayReady) return;

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);

  for (int i = 0; i < 6; i++) {
    display.setCursor(0, i * 10);
    display.println(helpPages[helpPage][i]);
  }

  display.display();
}

void sendPacket(uint8_t type, const uint8_t *payload,
                uint16_t length) {
  if (!client.connected()) return;

  uint8_t header[5] = {
    MAGIC_1,
    MAGIC_2,
    type,
    (uint8_t)(length & 0xFF),
    (uint8_t)(length >> 8)
  };

  client.write(header, sizeof(header));

  if (length > 0) {
    client.write(payload, length);
  }
}

void sendButtonEvent(uint8_t buttonId) {
  uint8_t payload[2] = {
    buttonId,
    (uint8_t)(talkEnabled ? 1 : 0)
  };

  sendPacket(PACKET_BUTTON, payload, sizeof(payload));
}

bool setupI2S() {
  i2s_config_t config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pins = {
    .bck_io_num = I2S_BCLK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  if (i2s_driver_install(I2S_PORT, &config, 0, nullptr) != ESP_OK) {
    Serial.println("ERROR: I2S driver installation failed");
    return false;
  }

  if (i2s_set_pin(I2S_PORT, &pins) != ESP_OK) {
    Serial.println("ERROR: I2S pin setup failed");
    return false;
  }

  i2s_zero_dma_buffer(I2S_PORT);
  Serial.println("I2S microphone initialized");
  return true;
}

void maintainNetwork() {
  uint32_t now = millis();
  wl_status_t status = WiFi.status();

  if (status != WL_CONNECTED) {
    if (wifiWasConnected) {
      Serial.println("WiFi connection lost");
      wifiWasConnected = false;
      client.stop();
    }

    if (now - lastWiFiAttempt >= 10000) {
    lastWiFiAttempt = now;

    Serial.print("WiFi status: ");
    Serial.println((int)status);

    Serial.println("Retrying WiFi connection...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    showStatus("Connecting WiFi", "Please wait");
}

    return;
  }

  if (!wifiWasConnected) {
    wifiWasConnected = true;
    Serial.println("SUCCESS: WiFi connected");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
    showStatus("WiFi connected", "Connecting laptop");
  }

  if (!client.connected() &&
      now - lastServerAttempt >= 3000) {
    lastServerAttempt = now;
    client.stop();

    Serial.print("Connecting to laptop: ");
    Serial.println(LAPTOP_IP);

    if (client.connect(LAPTOP_IP, LAPTOP_PORT)) {
      client.setNoDelay(true);
      Serial.println("SUCCESS: Laptop connected");
      showStatus("Laptop connected", "Waiting for Python");
    } else {
      Serial.println("Laptop TCP failed");
      showStatus("Laptop not found", "Check Python server");
    }
  }
}
void handlePythonStatus() {
  while (client.connected() && client.available() > 0) {
    char c = (char)client.read();
    Serial.print("Python status received: ");
    Serial.println(c);

    if (c == 'R') {
      appStopped = false;
      talkEnabled = false;
      digitalWrite(LED_PIN, LOW);
      showStatus("Ready", "Press TALK");
    } else if (c == 'L') {
      if (!appStopped)
        showStatus("Listening...", "Speak a command");
    } else if (c == 'I') {
      if (!appStopped)
        showStatus("Ready", talkEnabled ? "Mic active" : "Press TALK");
    } else if (c == 'D') {
      if (!appStopped)
        showStatus("Command done", "Ready for next");
    } else if (c == 'E') {
      if (!appStopped)
        showStatus("Not recognized", "Try again");
    } else if (c == 'X') {
      appStopped = true;
      talkEnabled = false;
      digitalWrite(LED_PIN, LOW);
      showStatus("Remote stopped", "Restart Python");
    }
  }
}

void handleTalkButton() {
  bool reading = digitalRead(BUTTON_TALK);
  uint32_t now = millis();

  if (reading != lastTalk && now - debounceTalk > DEBOUNCE_MS) {
    debounceTalk = now;
    lastTalk = reading;

    if (reading == LOW && !appStopped) {
      talkEnabled = !talkEnabled;
      digitalWrite(LED_PIN, talkEnabled ? HIGH : LOW);

      showStatus(talkEnabled ? "Listening..." : "Ready",
                 talkEnabled ? "Speak a command" : "Press TALK");

      sendButtonEvent(1);
    }
  }
}

void handleHelpButton() {
  bool reading = digitalRead(BUTTON_HELP);
  uint32_t now = millis();

  if (reading != lastHelp && now - debounceHelp > DEBOUNCE_MS) {
    debounceHelp = now;
    lastHelp = reading;

    if (reading == LOW && !appStopped) {
      helpMenuActive = true;
      helpPage = 0;
      showHelpPage();
      sendButtonEvent(2);
    }
  }
}

void handleNextButton() {
  bool reading = digitalRead(BUTTON_NEXT);
  uint32_t now = millis();

  if (reading != lastNext && now - debounceNext > DEBOUNCE_MS) {
    debounceNext = now;
    lastNext = reading;

    if (reading == LOW && !appStopped) {
      if (helpMenuActive) {
        helpPage = (helpPage + 1) % 4;
        showHelpPage();
      } else {
        sendButtonEvent(3);
        showStatus("Next", "Sending command");
      }
    }
  }
}

void handleSelectButton() {
  bool reading = digitalRead(BUTTON_SELECT);
  uint32_t now = millis();

  if (reading != lastSelect &&
      now - debounceSelect > DEBOUNCE_MS) {
    debounceSelect = now;
    lastSelect = reading;

    if (reading == LOW) {
      selectPressedAt = now;
      selectLongTriggered = false;
    } else if (!selectLongTriggered && !appStopped) {
      if (helpMenuActive) {
        helpMenuActive = false;
        showStatus("Ready", "Press TALK");
      } else {
        sendButtonEvent(4);
        showStatus("Select", "Sending command");
      }
    }
  }

  if (reading == LOW && lastSelect == LOW &&
      !selectLongTriggered && !appStopped &&
      now - selectPressedAt >= EXIT_HOLD_MS) {
    selectLongTriggered = true;
    talkEnabled = false;
    digitalWrite(LED_PIN, LOW);
    showStatus("Exiting remote", "Please wait");
    sendButtonEvent(5);
    appStopped = true;
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println("=== ESP32 WiFi Voice Remote ===");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  pinMode(BUTTON_TALK, INPUT_PULLUP);
  pinMode(BUTTON_HELP, INPUT_PULLUP);
  pinMode(BUTTON_NEXT, INPUT_PULLUP);
  pinMode(BUTTON_SELECT, INPUT_PULLUP);

  Wire.begin(OLED_SDA, OLED_SCL);
  displayReady = display.begin(0x3C, true);
  showStatus("Starting...", "WiFi voice remote");

  if (!displayReady) {
    Serial.println("WARNING: OLED initialization failed");
  } else {
    Serial.println("OLED initialized");
  }

  if (!setupI2S()) {
    showStatus("I2S setup failed", "Check mic pins");
    while (true) {
      delay(1000);
    }
  }

  Serial.println("Resetting WiFi...");
  WiFi.disconnect(true, true);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  delay(500);

  Serial.println();
  Serial.println("Scanning for WiFi networks...");

  int networkCount = WiFi.scanNetworks();

  if (networkCount == 0) {
    Serial.println("No WiFi networks found.");
  } else if (networkCount < 0) {
    Serial.printf("WiFi scan failed: %d\n", networkCount);
  } else {
    Serial.printf("Found %d networks:\n", networkCount);

    for (int i = 0; i < networkCount; i++) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" | Signal: ");
      Serial.print(WiFi.RSSI(i));
      Serial.println(" dBm");
    }
  }

  WiFi.scanDelete();

  Serial.println();
  Serial.println("Starting hotspot connection...");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  lastWiFiAttempt = millis();

  showStatus("Connecting WiFi", "Please wait");
}
void loop() {
  maintainNetwork();
  handlePythonStatus();

  handleTalkButton();
  handleHelpButton();
  handleNextButton();
  handleSelectButton();

  size_t bytesRead = 0;

  esp_err_t result = i2s_read(
    I2S_PORT,
    rawSamples,
    sizeof(rawSamples),
    &bytesRead,
    20 / portTICK_PERIOD_MS
  );

  if (result == ESP_OK && bytesRead > 0 &&
      talkEnabled && !appStopped && client.connected()) {
    int samplesCount = min(
      (int)(bytesRead / sizeof(int32_t)),
      AUDIO_SAMPLES
    );

    if (samplesCount == AUDIO_SAMPLES) {
      for (int i = 0; i < samplesCount; i++) {
        pcm[i] = (int16_t)(rawSamples[i] >> 16);
      }

      memcpy(audioPayload, pcm, AUDIO_BYTES);
      sendPacket(PACKET_AUDIO, audioPayload, AUDIO_BYTES);
    }
  }
}
