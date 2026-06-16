document.addEventListener("DOMContentLoaded", () => {

    const SUBJECTS = [
        ["TAMIL",   "tamil"],
        ["ENGLISH", "english"],
        ["MATHS",   "maths"],
        ["SCIENCE", "science"],
        ["SOCIAL",  "social"],
    ];

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

            marksTableBody.innerHTML = [
                ...SUBJECTS.map(([label, key]) => `<tr><td>${label}</td><td>${data[key]}</td></tr>`),
                `<tr><td><strong>TOTAL</strong></td><td><strong>${data.total}</strong></td></tr>`
            ].join("");

            studentName.textContent = `${data.name} (${data.regNo})`;
            marksDialog.showModal();
        });
    });

});