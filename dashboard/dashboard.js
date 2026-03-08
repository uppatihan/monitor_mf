document.addEventListener("DOMContentLoaded", async () => {
  const btnLogout = document.getElementById("btn-logout");
//   const dataTbody = document.getElementById("data-tbody");
//   const dataTitle = document.getElementById("data-title");

  // ตรวจสอบสถานะการล็อกอิน
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  if (!isLoggedIn) {
    alert("กรุณาเข้าสู่ระบบก่อนใช้งาน");
    window.location.href = "../login/login.html";
    return;
  }

  // ฟังก์ชันดึงข้อมูลใบงาน iMind (ล็อกอินใหม่เพื่อดึงข้อมูลล่าสุด)
  async function fetchImindCount() {
    const countElement = document.getElementById("ticket-count");
    const openElement = document.getElementById("ticket-open");

    const user = localStorage.getItem("loginUser");
    const pass = localStorage.getItem("loginPass");

    if (!user || !pass) {
      // ไม่มี credentials ใช้ข้อมูลจาก localStorage
      const rawData = localStorage.getItem("userData");
      if (rawData && countElement) {
        countElement.innerText = JSON.parse(rawData).length;
      }
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass })
      });
      const result = await res.json();
      if (result.success) {
        localStorage.setItem("userData", JSON.stringify(result.data || []));
        
        // จำนวนจากหน้าแรก (เหมือนตอนแรก)
        const firstPageCount = (result.data || []).length;
        // จำนวนทั้งหมดจาก API (เช่น 322)
        const totalOpen = result.total_group_open || "0";
        
        // แสดงผลในหน้าจอ
        if (countElement) countElement.innerText = firstPageCount;
        if (openElement) openElement.innerText = `รอปิด: ${totalOpen} รายการ`;
        
        // console.log(`📊 iMind Updated -> New: ${firstPageCount}, Open: ${totalOpen}`);
      }
    } catch (err) {
      console.error("Error fetching iMind:", err);
    }
  }

  // ฟังก์ชันดึงข้อมูลจาก Google Sheet (รวม F, H และผลต่าง)
  async function fetchGsheetCounts() {
    const elF = document.getElementById("gsheet-count");
    const elH = document.getElementById("gsheet-count-h");
    const elDiff = document.getElementById("gsheet-diff");
    const elValF = document.getElementById("gsheet-val-f");
    const elValH = document.getElementById("gsheet-val-h");

    try {
      const res = await fetch("http://localhost:5000/api/gsheet-counts");
      const data = await res.json();
      
      if (data.success) {
        if (elF) elF.innerText = data.count_f;
        if (elH) elH.innerText = data.count_h;
        if (elDiff) elDiff.innerText = data.diff;
        if (elValF) elValF.innerText = data.count_f;
        if (elValH) elValH.innerText = data.count_h;
      } else {
        const errorVal = "–";
        if (elF) elF.innerText = errorVal;
        if (elH) elH.innerText = errorVal;
        if (elDiff) elDiff.innerText = errorVal;
        if (elValF) elValF.innerText = "0";
        if (elValH) elValH.innerText = "0";
      }
    } catch (err) {
      console.error("Error fetching Google Sheet:", err);
      const errorVal = "–";
      if (elF) elF.innerText = errorVal;
      if (elH) elH.innerText = errorVal;
      if (elDiff) elDiff.innerText = errorVal;
    }
  }

  // ตัวแปรสำหรับเก็บ Interval ID
  let refreshIntervalId = null;

  // ฟังก์ชันหยุดการ Refresh
  function stopAutoRefresh() {
    if (refreshIntervalId) {
      clearInterval(refreshIntervalId);
      refreshIntervalId = null;
      // console.log("🛑 Interval Cleared");
    }
  }

  // ฟังก์ชันเริ่มการ Refresh อัตโนมัติ
  function startAutoRefresh() {
    stopAutoRefresh(); // Clear old one first
    
    // console.log("🚀 Starting Auto-refresh timer...");
    refreshIntervalId = setInterval(async () => {
      // Safety Check: ถ้าซ่อนอยู่ ให้หยุดทันที
      if (document.hidden) {
        // console.log("⚠️ Safety Triggered: Tab is hidden, stopping refresh.");
        stopAutoRefresh();
        return;
      }
      
      console.log("🔄");
      await fetchImindCount();
      await fetchGsheetCounts();
    }, 30000);
  }

  // ตรวจสอบการสลับแท็บเพื่อหยุด/เริ่ม Refresh
  document.addEventListener("visibilitychange", async () => {
    if (document.hidden) {
      // console.log("⏸️ Tab Hidden: หยุดการ Refresh อัตโนมัติ");
      stopAutoRefresh();
    } else {
      // console.log("▶️ Tab Visible: กลับมาเริ่ม Refresh อัตโนมัติ");
      // ดึงข้อมูลใหม่ทันที 1 ครั้งเมื่อกลับมา
      await fetchImindCount();
      await fetchGsheetCounts();
      startAutoRefresh();
    }
  });

  // ดึงข้อมูลครั้งแรกเมื่อโหลดหน้า
  await fetchImindCount();
  await fetchGsheetCounts();
  startAutoRefresh();

  // กดออกจากระบบ
  btnLogout.addEventListener("click", () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("userData");
    localStorage.removeItem("loginUser");
    localStorage.removeItem("loginPass");
    window.location.href = "../login/login.html";
  });
});
