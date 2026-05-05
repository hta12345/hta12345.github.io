// Yavaş ve Daha Ciddi Yıldız Animasyonu
const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d');

let width, height;
let stars = [];

function initStars() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    
    stars = [];
    const numStars = Math.floor((width * height) / 1500); 
    
    for(let i = 0; i < numStars; i++) {
        stars.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 1.2,
            vx: (Math.random() - 0.5) * 0.1, // Çok yavaş hareket
            vy: (Math.random() - 0.5) * 0.1, // Çok yavaş hareket
            alpha: Math.random() * 0.5 + 0.1
        });
    }
}

function drawStars() {
    ctx.clearRect(0, 0, width, height);
    
    stars.forEach(star => {
        star.x += star.vx;
        star.y += star.vy;
        
        if(star.x < 0) star.x = width;
        if(star.x > width) star.x = 0;
        if(star.y < 0) star.y = height;
        if(star.y > height) star.y = 0;
        
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${star.alpha})`;
        ctx.fill();
    });
    
    requestAnimationFrame(drawStars);
}

window.addEventListener('resize', initStars);
initStars();
drawStars();

// Sekme (Tab) Değiştirme Mantığı
const navBtns = document.querySelectorAll('.nav-btn');
const tabContents = document.querySelectorAll('.tab-content');

navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Aktif buton sınıfını güncelle
        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Hedef sekmeyi bul
        const targetId = btn.getAttribute('data-target');
        
        // İçerikleri gizle/göster
        tabContents.forEach(content => {
            if(content.id === targetId) {
                content.classList.add('active-tab');
            } else {
                content.classList.remove('active-tab');
            }
        });
    });
});

// --- FOTOĞRAF ÖNİZLEME (MODAL) MANTIĞI ---
const modal = document.getElementById("imageModal");
const modalImg = document.getElementById("img01");
const captionText = document.getElementById("caption");
const images = document.querySelectorAll(".patern-img");
const closeBtn = document.querySelector(".modal-close");

if (modal && modalImg && images.length > 0) {
    images.forEach(img => {
        img.addEventListener("click", function() {
            modal.classList.add("active");
            modalImg.src = this.src;
            captionText.innerHTML = this.alt; // Resmin alt özelliğini başlık olarak göster
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", function() {
            modal.classList.remove("active");
        });
    }

    // Arkaplana tıklanınca da modalı kapat
    modal.addEventListener("click", function(e) {
        if (e.target === modal) {
            modal.classList.remove("active");
        }
    });
}
