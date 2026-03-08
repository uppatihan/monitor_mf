document.addEventListener("DOMContentLoaded", () => {
    // อ้างอิงถึงปุ่ม Login และช่องกรอกข้อมูล
    const loginBtn = document.querySelector(".btn-login");
    const usernameInput = document.getElementById("txtUsername");
    const passwordInput = document.getElementById("txtPassword");

    // เมื่อมีการคลิกที่ปุ่ม Login
    loginBtn.addEventListener("click", async (e) => {
        // ดึงค่าที่กรอกมา
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // ตรวจสอบว่ามีข้อมูลหรือไม่
        if (!username || !password) {
            alert("⚠️ กรุณากรอก Username และ Password ให้ครบถ้วน");
            return;
        }

        // เปลี่ยนข้อความบนปุ่มระหว่างรอ
        const originalBtnText = loginBtn.innerText;
        loginBtn.innerText = "กำลังเข้าสู่ระบบ...";
        loginBtn.disabled = true;

        try {
            // ส่งข้อมูลไปยัง Python API (พอร์ต 5000)
            const response = await fetch("http://localhost:5000/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const result = await response.json();

            // แจ้งเตือนผลลัพธ์
            if (result.success) {
                // ตรวจสอบข้อมูลก่อนบันทึก
                const dataToSave = result.data || [];
                
                // บันทึกสถานะการล็อกอินและข้อมูล
                localStorage.setItem("isLoggedIn", "true");
                localStorage.setItem("userData", JSON.stringify(dataToSave));
                localStorage.setItem("loginUser", username);
                localStorage.setItem("loginPass", password);

                // alert(`✅ ล็อกอินสำเร็จ! \nกำลังพาท่านไปยังหน้า Dashboard...`);
                window.location.href = "../dashboard/dashboard.html";
            } else {
                alert(`❌ ล็อกอินล้มเหลว\n\n${result.message}`);
            }

        } catch (error) {
            console.error("Error:", error);
            alert("⚠️ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ Backend ได้ กรุณาตรวจสอบให้แน่ใจว่าได้รัน Python บนพอร์ต 5000 แล้ว");
        } finally {
            // คืนค่าปุ่มกลับมาเหมือนเดิม
            loginBtn.innerText = originalBtnText;
            loginBtn.disabled = false;
        }
    });

    // ให้กด Enter ในช่อง Password เพื่อล็อกอินได้เลย
    passwordInput.addEventListener("keyup", (event) => {
        if (event.key === "Enter") {
            loginBtn.click();
        }
    });
});
