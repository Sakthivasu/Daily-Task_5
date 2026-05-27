const API_URL = "http://127.0.0.1:5000";


// ================= LOGIN PAGE =================

function initLoginPage(){

    const form =
    document.getElementById("login-form");

    if(!form) return;

    form.addEventListener("submit", async function(e){

        e.preventDefault();

        const username =
        document.getElementById("username").value;

        const password =
        document.getElementById("password").value;

        const response = await fetch(
            `${API_URL}/login`,
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                credentials:"include",

                body:JSON.stringify({
                    username,
                    password
                })
            }
        );

        const data =
        await response.json();

        if(response.ok){

            window.location.href =
            "dashboard.html";

        } else {

            const error =
            document.getElementById("error-msg");

            error.innerText =
            data.message;

            error.classList.remove("hide");
        }
    });
}


// ================= REGISTER PAGE =================

function initRegisterPage(){

    const form =
    document.getElementById("register-form");

    if(!form) return;

    form.addEventListener("submit", async function(e){

        e.preventDefault();

        const username =
        document.getElementById("username").value;

        const email =
        document.getElementById("email").value;

        const password =
        document.getElementById("password").value;

        const confirmPassword =
        document.getElementById("confirm-password").value;

        if(password !== confirmPassword){

            alert("Passwords do not match");
            return;
        }

        const response = await fetch(
            `${API_URL}/register`,
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({
                    username,
                    email,
                    password
                })
            }
        );

        const data =
        await response.json();

        if(response.ok){

            alert("Registration Successful");

            window.location.href =
            "login.html";

        } else {

            const error =
            document.getElementById("error-msg");

            error.innerText =
            data.message;

            error.classList.remove("hide");
        }
    });
}


// ================= DASHBOARD PAGE =================

async function initDashboardPage(){

    const response = await fetch(
        `${API_URL}/expenses/summary`,
        {
            credentials:"include"
        }
    );

    if(!response.ok){

        window.location.href =
        "login.html";

        return;
    }

    const data =
    await response.json();

    document.getElementById("welcome-banner").innerText =
    `Welcome ${data.username} 👋`;

    document.getElementById("total-spent").innerText =
    `₹${data.total_amount}`;

    document.getElementById("total-count").innerText =
    data.total_expenses;

    document.getElementById("highest-expense").innerText =
    `₹${data.highest_expense}`;

    document.getElementById("categories-count").innerText =
    data.categories.length;


    // CATEGORY BARS

    const container =
    document.getElementById("category-bars-container");

    container.innerHTML = "";

    data.categories.forEach(cat => {

        container.innerHTML += `
            <div class="category-item">
                <p>${cat.category} - ₹${cat.total}</p>

                <div class="bar">
                    <div class="fill"
                    style="width:${cat.total}%">
                    </div>
                </div>
            </div>
        `;
    });


    // RECENT EXPENSES

    const expenseResponse = await fetch(
        `${API_URL}/expenses`,
        {
            credentials:"include"
        }
    );

    const expenses =
    await expenseResponse.json();

    const table =
    document.getElementById("recent-expenses-body");

    table.innerHTML = "";

    expenses.slice(0,5).forEach(exp => {

        table.innerHTML += `
            <tr>
                <td>${exp.title}</td>
                <td>${exp.category}</td>
                <td>₹${exp.amount}</td>
                <td>${exp.date}</td>
            </tr>
        `;
    });


    // LOGOUT

    document.getElementById("logout-btn")
    .addEventListener("click", logoutUser);
}



// ================= EXPENSE PAGE =================

function initExpensesPage(){

    const form =
    document.getElementById("expense-form");

    if(!form) return;


    // LOAD EXPENSES

    loadExpenses();


    // ADD EXPENSE

    form.addEventListener("submit",
    async function(e){

        e.preventDefault();

        const expense = {

            title:
            document.getElementById("title").value,

            amount:
            document.getElementById("amount").value,

            category:
            document.getElementById("category").value,

            date:
            document.getElementById("date").value,

            note:
            document.getElementById("note").value
        };

        const response = await fetch(
            `${API_URL}/expenses`,
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                credentials:"include",

                body:JSON.stringify(expense)
            }
        );

        const data =
        await response.json();

        if(response.ok){

            alert("Expense Added");

            form.reset();

           await  loadExpenses();

        } else {

            alert(data.message);
        }
    });


    // LOGOUT

    document.getElementById("logout-btn")
    .addEventListener("click", logoutUser);
}



// ================= LOAD EXPENSES =================

async function loadExpenses(){

    const table =
    document.getElementById("full-expenses-body");

    if(!table) return;

    const response = await fetch(
        `${API_URL}/expenses`,
        {
            credentials:"include"
        }
    );

    if(!response.ok){

        window.location.href =
        "login.html";

        return;
    }

    const expenses =
    await response.json();

    table.innerHTML = "";

    expenses.forEach(exp => {

        table.innerHTML += `
            <tr>
                <td>${exp.title}</td>
                <td>${exp.category}</td>
                <td>₹${exp.amount}</td>
                <td>${exp.date}</td>
                <td>${exp.note || ""}</td>

                <td>
                    <button
                    onclick="deleteExpense(${exp.id})"
                    class="btn-danger">
                    Delete
                    </button>
                </td>
            </tr>
        `;
    });
}



// ================= DELETE EXPENSE =================

async function deleteExpense(id){

    if(!confirm("Delete this expense?"))
    return;

    const response = await fetch(
        `${API_URL}/expenses/${id}`,
        {
            method:"DELETE",

            credentials:"include"
        }
    );

    const data =
    await response.json();

    if(response.ok){

        alert(data.message);

        loadExpenses();

    } else {

        alert(data.message);
    }
}



// ================= LOGOUT =================

async function logoutUser(){

    await fetch(
        `${API_URL}/logout`,
        {
            credentials:"include"
        }
    );

    window.location.href =
    "login.html";
}