#include <WiFi.h>
#include <WebServer.h>
#include <AccelStepper.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <ArduinoJson.h>
#include <math.h>

Preferences prefs;

const char *ssid = "Ghile";
const char *password = "ghilezan";
const char *HOSTNAME = "esp-multi";

// m1 - roof_left
// m2 - roof_right
// m3 - axis_x
// m4 - axis_y

// PUL- -> STEP_PIN, DIR- -> DIR_PIN, ENA- -> EN_PIN

// ---------------- PINI MOTOARE (din poza cu ESP32) ----------------
// Motor 1 - roof_left (stânga: P25 P26 P27)
#define M1_STEP 25
#define M1_DIR 26
#define M1_EN 27

// Motor 2 - roof_right (stânga: P14 P12 P13)
#define M2_STEP 14
#define M2_DIR 12
#define M2_EN 13

// Motor 3 - axis_x (dreapta: P5 P18 P19)
#define M3_STEP 5
#define M3_DIR 18
#define M3_EN 19

// Motor 4 - axis_y (dreapta: P16 P17 P21)
#define M4_STEP 16
#define M4_DIR 17
#define M4_EN 21

// -------------------------------------------------------------------

#define EN_ACTIVE_LOW 1

const long STEPS_PER_REV = 200;

WebServer server(8080); // server pe portul 8080

// ---------------- INTERFAȚĂ WEB (HTML + JS) ----------------
const char MAIN_page[] PROGMEM = R"rawliteral(
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>ESP32 Multi-Motor Control</title>
  <style>
    body { font-family: system-ui, Arial, sans-serif; background:#f5f5f5; margin:0; padding:20px; }
    h1 { margin-top:0; }
    .wrap { max-width:1200px; margin:0 auto; }
    .grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(250px,1fr)); gap:16px; margin-top:20px; }
    .card { background:#fff; border-radius:10px; padding:16px; box-shadow:0 2px 4px rgba(0,0,0,.08); }
    .title { font-weight:600; margin-bottom:8px; text-transform:capitalize; }
    label { display:block; font-size:13px; margin-top:8px; }
    input[type=number] { width:100%; padding:6px 8px; box-sizing:border-box; border-radius:6px; border:1px solid #ccc; }
    .row { display:flex; align-items:center; gap:8px; margin-top:6px; flex-wrap:wrap; }
    button { border:none; border-radius:999px; padding:6px 14px; cursor:pointer; font-size:13px; }
    .btn-move { background:#2563eb; color:#fff; }
    .btn-stop { background:#ef4444; color:#fff; }
    .btn-release { background:#9333ea; color:#fff; }
    .btn-stop-all { background:#111827; color:#fff; margin-top:16px; }
    .status { margin-top:6px; font-size:12px; color:#374151; }
    .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; }
    .on { background:#dcfce7; color:#166534; }
    .off { background:#fee2e2; color:#991b1b; }
    pre { background:#111827; color:#e5e7eb; padding:12px; border-radius:8px; font-size:11px; overflow:auto; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>🎛️ ESP32 Multi-Motor Control (HOLD + RELEASE)</h1>
  <p>Setează <strong>cm</strong>, viteză și direcție pentru fiecare motor și apasă <strong>MOVE</strong>.</p>
  <div class="grid"></div>
  <button class="btn-stop-all" onclick="emergencyStop()">EMERGENCY STOP 🚨</button>
  <button class="btn-release" onclick="releaseAll()" style="margin-left:10px;">RELEASE ALL 🔓</button>
  <h2>Log status JSON:</h2>
  <pre id="log"></pre>
</div>

<script>
const motors = ["roof_left","roof_right","axis_x","axis_y"];

function createCards() {
  const grid = document.querySelector('.grid');
  motors.forEach(name => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = `
      <div class="title">${name}</div>
      <div class="status">
        EN: <span id="en-${name}" class="badge off">OFF</span><br>
        Dir: <span id="dir-${name}">-</span> |
        Speed: <span id="sp-${name}">-</span> cm/s<br>
        Rămas: <span id="cm-${name}">-</span> cm
      </div>
      <label>Distanta (cm):</label>
      <input type="number" id="dist-${name}" min="0" step="0.1" value="10">
      <label>Viteza (cm/s):</label>
      <input type="number" id="speed-${name}" min="1" step="1" value="5">
      <label>Direcție:</label>
      <div class="row">
        <label><input type="radio" name="dir-${name}" value="1" checked> În față</label>
        <label><input type="radio" name="dir-${name}" value="0"> Înapoi</label>
      </div>
      <div class="row" style="margin-top:10px;">
        <button class="btn-move" onclick="moveMotor('${name}')">MOVE ▶️</button>
        <button class="btn-stop" onclick="stopMotor('${name}')">STOP ⏸️</button>
        <button class="btn-release" onclick="releaseMotor('${name}')">RELEASE 🔓</button>
      </div>
    `;
    grid.appendChild(div);
  });
}

async function moveMotor(name) {
  const cm = parseFloat(document.getElementById('dist-'+name).value || 0);
  const speed = parseFloat(document.getElementById('speed-'+name).value || 1);
  const dir = document.querySelector('input[name="dir-'+name+'"]:checked').value;
  const body = {};
  body[name] = { cm: cm, speed: speed, dir: parseInt(dir) };
  try {
    const res = await fetch('/api/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    document.getElementById('log').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    console.error(e);
  }
}

async function stopMotor(name) {
  try {
    const res = await fetch('/api/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motors: [name] })
    });
    const data = await res.json();
    document.getElementById('log').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    console.error(e);
  }
}

async function releaseMotor(name) {
  try {
    const res = await fetch('/api/release', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motors: [name] })
    });
    const data = await res.json();
    document.getElementById('log').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    console.error(e);
  }
}

async function releaseAll() {
  try {
    const res = await fetch('/api/release', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motors: "all" })
    });
    const data = await res.json();
    document.getElementById('log').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    console.error(e);
  }
}

async function emergencyStop() {
  try {
    const res = await fetch('/api/emergency_stop', {
      method: 'POST'
    });
    const data = await res.json();
    document.getElementById('log').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    console.error(e);
  }
}

async function refreshStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    document.getElementById('log').textContent = JSON.stringify(data, null, 2);
    motors.forEach(name => {
      const s = data[name];
      if (!s) return;
      const enEl = document.getElementById('en-'+name);
      if (s.en) {
        enEl.textContent = "ON (HOLD)";
        enEl.classList.remove('off');
        enEl.classList.add('on');
      } else {
        enEl.textContent = "OFF (RELEASED)";
        enEl.classList.remove('on');
        enEl.classList.add('off');
      }
      document.getElementById('dir-'+name).textContent = s.dir ? "în față" : "înapoi";
      document.getElementById('sp-'+name).textContent = s.sp_cm.toFixed(1);
      document.getElementById('cm-'+name).textContent = s.cm_rem.toFixed(2);
    });
  } catch (e) {
    // ignoră dacă dă fail, mai încearcă data viitoare
  }
}

createCards();
setInterval(refreshStatus, 500);
refreshStatus();
</script>
</body>
</html>
)rawliteral";

// ---------------- LOGICĂ MOTOR ----------------

struct Motor
{
    const char *name;
    AccelStepper *stepper;
    int enPin;
    bool enabled;
    float speed; // cm/s pentru API
    int dir;     // 1 = față, 0 = spate
    long target, start;

    // Parametri configurabili per motor
    int microstep;
    float mmPerRev;
    float maxSpeed; // cm/s

    Motor(const char *n, int sp, int dr, int en)
        : name(n), enPin(en), enabled(false), speed(5), dir(1), target(0), start(0),
          microstep(8), mmPerRev(40.0f), maxSpeed(30.0f)
    {
        stepper = new AccelStepper(AccelStepper::DRIVER, sp, dr);
    }

    float stepsPerMM() { return (STEPS_PER_REV * microstep) / mmPerRev; }
    float mmToSps(float v_mm) { return v_mm * stepsPerMM(); }
    long mmToSteps(float mm) { return (long)roundf(mm * stepsPerMM()); }

    void setEn(bool e)
    {
        enabled = e;
        digitalWrite(enPin, EN_ACTIVE_LOW ? (e ? LOW : HIGH) : (e ? HIGH : LOW));
        Serial.printf("[EN] %s -> %s (pin %d)\n", name, e ? "ON (HOLD)" : "OFF (RELEASED)", enPin);
    }

    // MODIFICAT: stop() oprește mișcarea DAR lasă motorul ENABLED (tare)
    void stop()
    {
        target = 0;
        stepper->setSpeed(0);
        // NU mai facem setEn(false) aici!
        Serial.printf("[STOP] Motor %s oprit (dar rămâne HOLD)\n", name);
    }

    // NOU: release() relaxează motorul (moale)
    void release()
    {
        target = 0;
        stepper->setSpeed(0);
        setEn(false); // Acum dezactivăm motorul
        Serial.printf("[RELEASE] Motor %s relaxat (MOALE)\n", name);
    }

    // mm      -> distanța în mm
    // spd_cm  -> viteză în cm/s
    void moveMM(float mm, float spd_cm, int d)
    {
        float spd_mm = spd_cm * 10.0f; // cm/s -> mm/s
        speed = constrain(spd_cm, 1.0f, maxSpeed);
        dir = d ? 1 : 0;
        target = mmToSteps(mm);
        start = stepper->currentPosition();
        stepper->setSpeed(dir ? mmToSps(spd_mm) : -mmToSps(spd_mm));
        setEn(true); // Activează motorul
        Serial.printf("[MOVE] %s: dist=%.2f mm (%.2f cm) speed=%.1f cm/s dir=%s steps=%ld\n",
                      name, mm, mm / 10.0f, speed, dir ? "FWD" : "REV", target);
    }

    void moveCM(float cm, float spd_cm, int d)
    {
        float mm = cm * 10.0f;
        moveMM(mm, spd_cm, d);
    }

    // MODIFICAT: când ajunge la target, NU mai face stop() automat
    void update()
    {
        if (enabled && target > 0)
        {
            if (abs(stepper->currentPosition() - start) >= target)
            {
                Serial.printf("[DONE] %s: target atins (motor rămâne HOLD)\n", name);
                target = 0;           // Marchează că am ajuns
                stepper->setSpeed(0); // Oprește mișcarea
                                      // DAR motorul rămâne enabled (tare)!
            }
            else
            {
                stepper->runSpeed();
            }
        }
    }

    float remainMM()
    {
        return target > 0 ? (target - abs(stepper->currentPosition() - start)) / stepsPerMM() : 0;
    }

    float remainCM()
    {
        return remainMM() / 10.0f;
    }

    void loadConfig()
    {
        prefs.begin("motor", true);
        String key = String(name);
        mmPerRev = prefs.getFloat((key + "_mmrev").c_str(), 40.0f);
        microstep = prefs.getInt((key + "_ms").c_str(), 8);
        maxSpeed = prefs.getFloat((key + "_max").c_str(), 30.0f); // cm/s
        prefs.end();
        stepper->setMaxSpeed(mmToSps(maxSpeed * 10.0f * 2)); // 2x viteza max în mm/s
        Serial.printf("[CFG-LOAD] %s: mmrev=%.2f ms=%d max=%.1f cm/s steps/mm=%.2f\n",
                      name, mmPerRev, microstep, maxSpeed, stepsPerMM());
    }

    void saveConfig()
    {
        prefs.begin("motor", false);
        String key = String(name);
        prefs.putFloat((key + "_mmrev").c_str(), mmPerRev);
        prefs.putInt((key + "_ms").c_str(), microstep);
        prefs.putFloat((key + "_max").c_str(), maxSpeed);
        prefs.end();
        stepper->setMaxSpeed(mmToSps(maxSpeed * 10.0f * 2));
        Serial.printf("[CFG-SAVE] %s: mmrev=%.2f ms=%d max=%.1f cm/s\n",
                      name, mmPerRev, microstep, maxSpeed);
    }
};

Motor m1("roof_left", M1_STEP, M1_DIR, M1_EN);
Motor m2("roof_right", M2_STEP, M2_DIR, M2_EN);
Motor m3("axis_x", M3_STEP, M3_DIR, M3_EN);
Motor m4("axis_y", M4_STEP, M4_DIR, M4_EN);

Motor *motors[] = {&m1, &m2, &m3, &m4};
const int MOTOR_COUNT = 4;

Motor *findMotor(const char *name)
{
    for (int i = 0; i < MOTOR_COUNT; i++)
        if (strcmp(motors[i]->name, name) == 0)
            return motors[i];
    return nullptr;
}

void stopAllMotors()
{
    for (int i = 0; i < MOTOR_COUNT; i++)
        motors[i]->stop();
}

// NOU: release all motors
void releaseAllMotors()
{
    for (int i = 0; i < MOTOR_COUNT; i++)
        motors[i]->release();
}

// ---------------- API HANDLERS ----------------

void apiMove()
{
    String body = server.arg("plain");
    Serial.printf("[HTTP] /api/move body: %s\n", body.c_str());

    StaticJsonDocument<1024> doc;
    if (deserializeJson(doc, body))
    {
        server.send(400, "application/json", "{\"error\":\"bad json\"}");
        Serial.println("[HTTP] /api/move - JSON invalid");
        return;
    }

    String resp = "{\"moved\":[";
    int cnt = 0;

    for (int i = 0; i < MOTOR_COUNT; i++)
    {
        if (doc.containsKey(motors[i]->name))
        {
            auto cmd = doc[motors[i]->name];
            float cm = cmd["cm"] | 0;    // distanță în cm
            float sp = cmd["speed"] | 5; // cm/s
            int d = cmd["dir"] | 1;      // 1 = față, 0 = spate

            if (cm > 0 && cm <= 1000)
            {
                motors[i]->moveCM(cm, sp, d);
                if (cnt > 0)
                    resp += ",";
                resp += "\"" + String(motors[i]->name) + "\"";
                cnt++;
            }
            else
            {
                Serial.printf("[WARN] %s: cm invalid=%.2f\n", motors[i]->name, cm);
            }
        }
    }

    resp += "]}";
    server.send(200, "application/json", resp);
}

// MODIFICAT: stop() oprește mișcarea dar lasă motorul HOLD
void apiStop()
{
    String body = server.arg("plain");
    Serial.printf("[HTTP] /api/stop body: %s\n", body.c_str());

    StaticJsonDocument<512> doc;
    if (deserializeJson(doc, body))
    {
        // JSON prost -> tot stop
        stopAllMotors();
        server.send(200, "application/json", "{\"stopped\":\"all\",\"note\":\"motors remain HOLD\"}");
        Serial.println("[HTTP] /api/stop -> all (motors HOLD)");
        return;
    }

    if (doc["motors"] == "all")
    {
        stopAllMotors();
        server.send(200, "application/json", "{\"stopped\":\"all\",\"note\":\"motors remain HOLD\"}");
        Serial.println("[HTTP] /api/stop -> all (motors HOLD)");
    }
    else if (doc["motors"].is<JsonArray>())
    {
        for (auto v : doc["motors"].as<JsonArray>())
        {
            const char *name = v.as<const char *>();
            Motor *m = findMotor(name);
            if (m)
            {
                m->stop();
                Serial.printf("[HTTP] /api/stop -> %s (motor HOLD)\n", name);
            }
            else
            {
                Serial.printf("[HTTP] /api/stop -> %s (NOT FOUND)\n", name);
            }
        }
        server.send(200, "application/json", "{\"ok\":true,\"note\":\"motors remain HOLD\"}");
    }
    else
    {
        server.send(400, "application/json", "{\"error\":\"bad json or motors\"}");
    }
}

// NOU: /api/release - relaxează motoarele (moale)
void apiRelease()
{
    String body = server.arg("plain");
    Serial.printf("[HTTP] /api/release body: %s\n", body.c_str());

    StaticJsonDocument<512> doc;
    if (deserializeJson(doc, body))
    {
        // JSON prost -> release all
        releaseAllMotors();
        server.send(200, "application/json", "{\"released\":\"all\"}");
        Serial.println("[HTTP] /api/release -> all");
        return;
    }

    if (doc["motors"] == "all")
    {
        releaseAllMotors();
        server.send(200, "application/json", "{\"released\":\"all\"}");
        Serial.println("[HTTP] /api/release -> all");
    }
    else if (doc["motors"].is<JsonArray>())
    {
        for (auto v : doc["motors"].as<JsonArray>())
        {
            const char *name = v.as<const char *>();
            Motor *m = findMotor(name);
            if (m)
            {
                m->release();
                Serial.printf("[HTTP] /api/release -> %s\n", name);
            }
            else
            {
                Serial.printf("[HTTP] /api/release -> %s (NOT FOUND)\n", name);
            }
        }
        server.send(200, "application/json", "{\"ok\":true}");
    }
    else
    {
        server.send(400, "application/json", "{\"error\":\"bad json or motors\"}");
    }
}

// MODIFICAT: emergency stop face release (motoare moale)
void apiEmergencyStop()
{
    Serial.println("[HTTP] /api/emergency_stop");
    releaseAllMotors(); // Emergency stop = release all
    server.send(200, "application/json", "{\"emergency_stop\":true,\"released\":true}");
}

void apiStatus()
{
    String json = "{";

    for (int i = 0; i < MOTOR_COUNT; i++)
    {
        if (i > 0)
            json += ",";
        json += "\"" + String(motors[i]->name) + "\":{";
        json += "\"en\":" + String(motors[i]->enabled ? "true" : "false") + ",";
        json += "\"sp_cm\":" + String(motors[i]->speed, 1) + ",";
        json += "\"dir\":" + String(motors[i]->dir) + ",";
        json += "\"cm_rem\":" + String(motors[i]->remainCM(), 2) + ",";
        json += "\"cfg\":{";
        json += "\"mmrev\":" + String(motors[i]->mmPerRev, 2) + ",";
        json += "\"ms\":" + String(motors[i]->microstep) + ",";
        json += "\"max_cm\":" + String(motors[i]->maxSpeed, 1) + ",";
        json += "\"steps_mm\":" + String(motors[i]->stepsPerMM(), 2);
        json += "}}";
    }

    json += "}";
    server.send(200, "application/json", json);
}

void apiConfig()
{
    String body = server.arg("plain");
    Serial.printf("[HTTP] /api/config body: %s\n", body.c_str());

    StaticJsonDocument<512> doc;
    if (deserializeJson(doc, body))
    {
        server.send(400, "text/plain", "bad json");
        Serial.println("[HTTP] /api/config - JSON invalid");
        return;
    }

    for (int i = 0; i < MOTOR_COUNT; i++)
    {
        Motor *m = motors[i];
        if (doc.containsKey(m->name))
        {
            auto cfg = doc[m->name];
            if (cfg.containsKey("mm_per_rev"))
                m->mmPerRev = cfg["mm_per_rev"];
            if (cfg.containsKey("microstep"))
                m->microstep = cfg["microstep"];
            if (cfg.containsKey("max_speed"))
                m->maxSpeed = cfg["max_speed"]; // cm/s
            m->saveConfig();
        }
    }

    apiStatus();
}

// ---------------- SETUP / LOOP ----------------

void setup()
{
    Serial.begin(115200);
    delay(200);
    Serial.println("=== ESP32 Multi-Motor Control (HOLD + RELEASE) ===");

    pinMode(M1_EN, OUTPUT);
    pinMode(M2_EN, OUTPUT);
    pinMode(M3_EN, OUTPUT);
    pinMode(M4_EN, OUTPUT);

    m1.setEn(false);
    m2.setEn(false);
    m3.setEn(false);
    m4.setEn(false);

    for (int i = 0; i < MOTOR_COUNT; i++)
    {
        motors[i]->loadConfig();
    }

    WiFi.begin(ssid, password);
    Serial.printf("Conectare la WiFi '%s'...\n", ssid);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(250);
        Serial.print('.');
    }

    Serial.println();
    Serial.printf("[NET] IP: %s\n", WiFi.localIP().toString().c_str());

    if (MDNS.begin(HOSTNAME))
    {
        Serial.printf("[mDNS] raspunde ca http://%s.local:8080/\n", HOSTNAME);
    }
    else
    {
        Serial.println("[mDNS] EROARE start");
    }

    server.on("/", HTTP_GET, []()
              { server.send_P(200, "text/html", MAIN_page); });

    server.on("/api/move", HTTP_POST, apiMove);
    server.on("/api/stop", HTTP_POST, apiStop);
    server.on("/api/release", HTTP_POST, apiRelease); // NOU!
    server.on("/api/emergency_stop", HTTP_POST, apiEmergencyStop);
    server.on("/api/status", HTTP_GET, apiStatus);
    server.on("/api/config", HTTP_POST, apiConfig);

    server.begin();
    Serial.println("[HTTP] Server pornit pe portul 8080");
    Serial.println("[INFO] Motoarele rămân HOLD după mișcare - folosește /api/release pentru a relaxa");
}

void loop()
{
    server.handleClient();
    for (int i = 0; i < MOTOR_COUNT; i++)
        motors[i]->update();
}
