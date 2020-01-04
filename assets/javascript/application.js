var navButtons

function addNavButtons(){
    if (navButtons == undefined ) return
    for(let i=0; i < navButtons.length; i++)
    {
        button = document.createElement("button")
        button.classList.add("nvButton")
        button.classList.add(navButtons[i][2])
        button.style.float = navButtons[i][3]
        button.innerText = navButtons[i][0]
        button.onmousedown = function(){
            eval(navButtons[i][1])
        }

        document.getElementById('navFooter').appendChild(button)
    }
}

