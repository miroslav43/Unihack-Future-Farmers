// TEST: Schimbă EN_ACTIVE_LOW pentru a testa
// Linia 36 în codul tău:

// VARIANTA 1 (actuală):
#define EN_ACTIVE_LOW 1  // LOW = ON, HIGH = OFF

// Dacă motoarele rămân tari după release, încearcă:
// VARIANTA 2:
// #define EN_ACTIVE_LOW 0  // HIGH = ON, LOW = OFF

/*
INSTRUCȚIUNI:

1. În Arduino IDE, deschide ESP32_MODIFIED_CODE.ino
2. Găsește linia 36: #define EN_ACTIVE_LOW 1
3. Schimbă-o în: #define EN_ACTIVE_LOW 0
4. Upload la ESP32
5. Test release din UI
6. Dacă tot nu funcționează, schimbă înapoi la 1

EXPLICAȚIE:
- Unele driver-uri DRV8825/A4988 au EN pin "active low" (LOW = enabled)
- Altele au EN pin "active high" (HIGH = enabled)
- Depinde de driver-ul fizic
*/

// ===== SAU VERIFICĂ CONEXIUNILE =====
// Asigură-te că pinii EN sunt conectați corect:

// Motor 1 - roof_left:  EN pin 27 → ENA- pe driver
// Motor 2 - roof_right: EN pin 13 → ENA- pe driver
// Motor 3 - axis_x:     EN pin 19 → ENA- pe driver
// Motor 4 - axis_y:     EN pin 21 → ENA- pe driver

// Dacă ENA- nu e conectat deloc, motorul va rămâne mereu enabled!

