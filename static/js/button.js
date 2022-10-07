function toggleLightDarkMode(button) {
    body = document.body
    if(button.checked){
        body.classList.remove('light')
        body.classList.add('dark')
    }
    else {
        body.classList.remove('dark')
        body.classList.add('light')
    }
}

function changeButtonState(button, playURL, pauseURL) {
    if(button.getAttribute('state') != "true")
    {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", playURL);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");   
        xhr.onload = () => {
            if(xhr.status != 200) {
                console.log("Error: " + xhr.status)
                button.classList.remove('pre-active')
            }
            else {
                button.setAttribute('state', 'true')
                button.classList.add('active')
                //button.style.backgroundColor = 'var(--active)'
                //button.style.color = 'white'
            }
        }
        xhr.send(`{"uri": "${button.getAttribute('uri')}"}`)
        Array.from(document.getElementsByClassName('playlist-button')).forEach((instance) => {
            instance.classList.remove('active')

            if(instance != button) {
                instance.setAttribute('state', 'false')
                // instance.style.backgroundColor = 'var(--off)'
                instance.classList.remove('pre-active')
            }
            else {
                // instance.style.backgroundColor = 'var(--changing)'
                instance.classList.add('pre-active')
            }
            // instance.style.color = 'inherit'
        })
    }
    else {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", pauseURL);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");   
        xhr.onload = () => {
            if(xhr.status != 200) {
                console.log("Error: " + xhr.status)
                button.classList.add('active')
            }
            else {
                button.setAttribute('state', 'false')
                button.classList.remove('pre-active')
            }
        }
        xhr.send(`{"uri": "${button.getAttribute('uri')}"}`)
        button.classList.remove('active')
    }
}