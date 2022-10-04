function changeButtonState(button, playURL) {
    if(button.getAttribute('state') != "true")
    {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", playURL);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");   
        xhr.onload = () => {
            if(xhr.status != 200) {
                console.log("Error: " + xhr.status)
            }
            else {
                button.setAttribute('state', 'true')
                button.style.backgroundColor = 'var(--active)'
                button.style.color = 'white'
            }
        }
        xhr.send(`{"uri": "${button.getAttribute('uri')}"}`)
        Array.from(document.getElementsByClassName('playlist-button')).forEach((instance) => {
            if(instance != button) {
                instance.setAttribute('state', 'false')
                instance.style.backgroundColor = 'var(--off)'
            }
            else {
                instance.style.backgroundColor = 'var(--changing)'
            }
            instance.style.color = 'inherit'
        })
    }
}