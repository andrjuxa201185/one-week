$(document).ready(function() {
    $("#q").typeahead({
            highlight: true,
            minLength: 1
        },{
            display: function(suggestion) { return suggestion.header; },
            limit: 10,
            source: search,
            templates: {
                suggestion: Handlebars.compile(
                    "<div class='typeahead'>{{header}}</div>"
                )
            }
    });


    $.getJSON('/bookmarks', function(data){
        document.getElementById('spanCountAppleBM').innerHTML = data["count"];
        document.getElementsByClassName('span-bookmarks-count')[0].innerHTML = data["count"];
    });

    let buttonSearch = document.getElementById('b');
    let form = document.getElementById('formRegLog');
    let checkbox_register = document.getElementsByName('checkboxRegister')[0];
    let checkbox_login = document.getElementsByName('checkboxLogin')[0];
    let apples = document.getElementsByClassName('img-apple2');
    

    [].forEach.call(apples, function(apple, i, apples) {
        apple.addEventListener("click", addDelBookmark);
    });

    let formAddEdit = document.getElementById('formAdd');

    if (formAddEdit){
        formAddEdit.addEventListener('input', subDisabled)};
    if (buttonSearch){
        buttonSearch.addEventListener('click', show_search);};
    if (form){
        form.addEventListener('submit', checkPasswords);};
    if (checkbox_register){
        checkbox_register.addEventListener('change', showPassword2);};
    if (checkbox_login){
        checkbox_login.addEventListener('change', showPassword);};
});

function showPassword(){
    let password = document.getElementsByName('password')[0];
    let checkbox = document.getElementById('exampleCheck2');
    if (checkbox.checked){
        password.type = 'text';
    } else {
        password.type = 'password';
    };
    password.focus();
};

function showPassword2(){
    let password = document.getElementsByName('password')[0];
    let password2 = document.getElementsByName('password2')[0];
    let checkbox = document.getElementById('exampleCheck1');
    if (checkbox.checked){
        password.type = 'text';
        password2.type = 'text';
    } else {
        password.type = 'password';
        password2.type = 'password';
    };
    password.focus();
};

function checkPasswords(event){
    let password = document.getElementsByName('password')[0].value;
    let password2 = document.getElementsByName('password2')[0].value;
    if (password != password2){
        event.preventDefault();
        alert('Пароли не совпадают!');
    };
    password.focus();
};

function search(query, syncResults, asyncResults){
    $.getJSON("/search", {q: query}, function(data, textStatus, jqXHR) {
        asyncResults(data);
    });
};

function show_search(){
    let query = document.getElementById('q').value;
    if (query){
        query = "?q=" + query;
        window.location.href = '/show_search' + query;
    };
};

function addDelBookmark(e){
    let el = e.target;
    setTimeout(function(){
        if (el.style.opacity == 0){
        el.style.opacity = 1;
        el.removeAttribute("title");
        el.setAttribute("title","удалить из закладок");
        let add = el.dataset.id;
        $.getJSON('/bookmarks', {add: add}, function(data){
            document.getElementsByClassName('span-bookmarks-count')[0].innerHTML = data["count"];
            document.getElementById('spanCountAppleBM').innerHTML = data["count"];
        });
    } else {
        el.style.opacity = 0;
        el.removeAttribute("title");
        el.setAttribute("title","добавить в закладки");
        let del = el.dataset.id;
        $.getJSON('/bookmarks', {del: del}, function(data){
            document.getElementsByClassName('span-bookmarks-count')[0].innerHTML = data["count"];
            document.getElementById('spanCountAppleBM').innerHTML = data["count"];
        });
    }}, 
    200);
    
};

function subDisabled(){
    let validEl = document.getElementsByClassName('valid');
    let button = document.getElementById('submit');
    let flag = true;

    for (let i = 0; i < validEl.length; i++){
        if (validEl[i].value === "" || validEl[i].value == undefined){
            flag = false;
            button.setAttribute("disabled", "disabled");
        };
    };
    if (flag) {
        button.removeAttribute("disabled");
    };
};
