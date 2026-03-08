// visibility_tracker.js
// ระบบตรวจสอบว่าผู้ใช้มีการสลับแท็บไปที่อื่นหรือไม่ และใช้เวลานานเท่าไหร่

let hiddenStartTime = 0;

const formatTime = (date) => date.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });

const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
  const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
};

document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    // เมื่อผู้ใช้ย้ายไปแท็บอื่นหรือย่อหน้าต่าง
    hiddenStartTime = Date.now();
    console.log(`%c[Tab Hidden] 🔴 : ${formatTime(new Date())}`, "color: #ff4d4d; font-weight: bold;");
  } else {
    // เมื่อผู้ใช้กลับมาที่แท็บเดิม
    if (hiddenStartTime !== 0) {
      const awayDurationSeconds = (Date.now() - hiddenStartTime) / 1000;
      const durationString = formatDuration(awayDurationSeconds);
      
      console.log(`%c[Tab Visible] 🟢 : ${formatTime(new Date())}`, "color: #00ff00; font-weight: bold;");
      console.log(`%c[Duration] ⏱️ : ${durationString} (HH:MM:SS)`, "background: #b012ffff; color: #fff; padding: 2px 5px; border-radius: 4px;");
      
      // รีเซ็ตการจับเวลา
      hiddenStartTime = 0;
    }
  }
});

// console.log("👁️ Visibility Tracker");
console.log(" 👁️ ");

