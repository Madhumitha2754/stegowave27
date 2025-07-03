document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("backgroundCanvas");
    const ctx = canvas.getContext("2d");

    let w, h;
    function resizeCanvas() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    // Particle System
    const particles = [];
    const shootingStars = [];

    function createParticles(count) {
        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                radius: Math.random() * 3 + 1,
                dx: (Math.random() - 0.5) * 2,
                dy: (Math.random() - 0.5) * 2,
                color: `hsl(${Math.random() * 360}, 100%, 70%)`
            });
        }
    }

    function drawParticles() {
        ctx.clearRect(0, 0, w, h);

        // Draw and Move Particles
        particles.forEach((p, index) => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();

            p.x += p.dx;
            p.y += p.dy;

            if (p.x < 0 || p.x > w) p.dx *= -1;
            if (p.y < 0 || p.y > h) p.dy *= -1;

            // Neon Lines Between Close Particles
            for (let j = index + 1; j < particles.length; j++) {
                let p2 = particles[j];
                let distance = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(0, 255, 238, ${1 - distance / 100})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        });

        // Shooting Stars
        if (Math.random() < 0.02) {
            shootingStars.push({
                x: Math.random() * w,
                y: Math.random() * h / 2,
                speed: Math.random() * 4 + 2
            });
        }
        for (let i = 0; i < shootingStars.length; i++) {
            let s = shootingStars[i];
            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            ctx.lineTo(s.x + 10, s.y + 10);
            ctx.strokeStyle = "rgba(255, 255, 0, 0.8)";
            ctx.lineWidth = 2;
            ctx.stroke();
            s.x += s.speed;
            s.y += s.speed;
            if (s.x > w || s.y > h) shootingStars.splice(i, 1);
        }

        requestAnimationFrame(drawParticles);
    }

    createParticles(80);
    drawParticles();
});
