document.addEventListener("DOMContentLoaded", () => {

    const grpdtls = [
        {
            name: "COMPUTER SCIENCE + MATHS",
            code: "csc",
            sub1: "PHY",
            sub2: "CHEM",
            sub3: "COMP",
            sub4: "MATHS",
        },
        {
            name: "BIOLOGY + MATHS",
            code: "biomat",
            sub1: "PHY",
            sub2: "CHEM",
            sub3: "BIO",
            sub4: "MATHS",
        },
        {
            name: "BIOLOGY + COMP",
            code: "biocs",
            sub1: "PHY",
            sub2: "CHEM",
            sub3: "BIO",
            sub4: "COMP",
        },
        {
            name: "ARTS / CA",
            code: "artsca",
            sub1: "ECO",
            sub2: "COM",
            sub3: "ACC",
            sub4: "CA",
        },
        {
            name: "ARTS / BM",
            code: "artsbm",
            sub1: "ECO",
            sub2: "COM",
            sub3: "ACC",
            sub4: "BM",
        },
        {
            name: "BME + MATHS",
            code: "bme",
            sub1: "MATHS",
            sub2: "BME (THY)",
            sub3: "BME (PRT)",
            sub4: "ES",
        }
    ];

    const groupMap = Object.fromEntries(grpdtls.map(g => [g.code, g]));

    const dialogHtml = `
    <dialog id="marksDialog">
        <h3 id="studentName"></h3>
        <table border="1">
            <thead>
                <tr><th>SUBJECT</th><th>MARK</th></tr>
            </thead>
            <tbody id="marksTableBody"></tbody>
        </table>
        <br>
        <form method="dialog">
            <button>OK</button>
        </form>
    </dialog>`;

    document.getElementById("dias").innerHTML = dialogHtml;

    const marksDialog = document.getElementById("marksDialog");
    const studentName = document.getElementById("studentName");
    const marksTableBody = document.getElementById("marksTableBody");

    document.querySelectorAll(".view-btn").forEach(button => {
        button.addEventListener("click", () => {
            const data = button.dataset;
            const group = groupMap[data.group];

            const rows = [
                [data.langName,  data.lang],
                ["ENG",          data.eng],
                [group.sub1,     data.sub1],
                [group.sub2,     data.sub2],
                [group.sub3,     data.sub3],
                [group.sub4,     data.sub4],
                ["TOTAL",        data.total],
                ["CUT OFF",      data.cutoff],
            ];

            marksTableBody.innerHTML = rows
                .map(([sub, mark]) => `<tr><td>${sub}</td><td>${mark}</td></tr>`)
                .join("");

            studentName.textContent = `${data.name} (${data.regNo})`;
            marksDialog.showModal();
        });
    });

});


// Pass percentage circle animation
(function () {
    const circleEl = document.querySelector('.pass_percent_circle');
    const appeared = parseInt(circleEl.dataset.appeared);
    const passed   = parseInt(circleEl.dataset.passed);
    const pct = ((passed / appeared) * 100).toFixed(2);

    const circle = document.getElementById('progressCircle');
    const label  = document.getElementById('percentValue');
    const circumference = 326.7;

    const svgEl = circle.closest('svg');
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = `
        <linearGradient id="circleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#22c55e"/>
            <stop offset="100%" stop-color="#0d9488"/>
        </linearGradient>`;
    svgEl.prepend(defs);

    setTimeout(() => {
        const offset = circumference - (parseFloat(pct) / 100) * circumference;
        circle.style.strokeDashoffset = offset;

        let current = 0;
        const step = parseFloat(pct) / 60;
        const counter = setInterval(() => {
            current = Math.min(current + step, parseFloat(pct));
            label.textContent = current.toFixed(2) + '%';
            if (current >= parseFloat(pct)) clearInterval(counter);
        }, 1000 / 60);
    }, 300);
})();