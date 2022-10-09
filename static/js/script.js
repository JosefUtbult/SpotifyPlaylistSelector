function log(msg) {
    document.getElementById("status").innerHTML = msg;
    console.error(msg);
}

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

function setCookie() {
    file = document.getElementById("settings-input")
    if(file.files.length)
    {
        var reader = new FileReader();
        reader.onload = function(e) {
            try {
                settings = JSON.parse(e.target.result)
                
                if(settings["spotify_client_id"] === undefined) {
                    log("Spotify client ID not specified in settings")
                }
                else if(settings["spotify_client_secret"] === undefined) {
                    log("Spotify client secret not specified in settings")
                }
                else if(settings["darkmode"] === undefined) {
                    log("Darkmode flag not specified in settings")
                }
                else if(settings["playlists"] === undefined) {
                    log("Playlists not specified in settings")
                }
                else if(!Array.isArray(settings["playlists"])) {
                    log("Malformed playlist list")
                }
                else {
                    var now = new Date();
                    var time = now.getTime();
                    var expireTime = time + 365.25*1000*36000;
                    now.setTime(expireTime);

                    document.cookie = 'Settings='+ JSON.stringify(settings) +';expires='+now.toUTCString()+';path=/;SameSite=Strict'
                }
                

            } catch (error) {
                log(error)
            }    
        };

        reader.readAsBinaryString(file.files[0]);
    }
}

function getSettings() {
    try {
        const regex = /Settings=([^;]*)/gm;
        return JSON.parse(regex.exec(document.cookie)[1])
    } catch (error) {
        log(error)
    } 
}

function changeButtonState(buttonId, playURL, pauseURL) {
    button = document.getElementById(buttonId)
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
            }
        }
        
        settings = getSettings()
        xhr.send(JSON.stringify({
            spotify_client_id: settings.spotify_client_id,
            spotify_client_secret: settings.spotify_client_secret,
            uri: button.getAttribute('uri')
        }))

        Array.from(document.getElementsByClassName('playlist-button')).forEach((instance) => {
            instance.classList.remove('active')

            if(instance != button) {
                instance.setAttribute('state', 'false')
                instance.classList.remove('pre-active')
            }
            else {
                instance.classList.add('pre-active')
            }
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
        
        settings = getSettings()
        xhr.send(JSON.stringify({
            spotify_client_id: settings.spotify_client_id,
            spotify_client_secret: settings.spotify_client_secret,
            uri: button.getAttribute('uri')
        }))

        button.classList.remove('active')
    }
}

window.onload = () => {
    buttonContainer = document.getElementById("button-container")
    settings = getSettings()
    buttons = new Array()
    settings.playlists.forEach((instance, index) => {
        button = document.createElement('button');
        button.classList.add("button")
        button.classList.add("playlist-button")
        button.id = `playlist-button-${index}`
        button.onclick = () => { changeButtonState(`playlist-button-${index}`, '/play', '/pause') }
        button.setAttribute('uri', instance)
        button.setAttribute('state', false)

        // TODO: Make this not be a syncronus call
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/get-playlist-name", false);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");   
        xhr.onload = () => {
            if(xhr.status != 200) {
                console.log("Error: " + xhr.status)
            }
            else {
                // TODO: Make the buttons appear all at once
            }
        }
        xhr.send(JSON.stringify({
            spotify_client_id: settings.spotify_client_id,
            spotify_client_secret: settings.spotify_client_secret,
            uri: instance
        }))
        button.innerHTML = JSON.parse(xhr.responseText)['name']
        buttons.push(button)
        // <button class="button playlist-button" onclick="changeButtonState(this, '{{ url_for('play') }}', '{{ url_for('pause') }}')" uri="{{ playlist['uri'] }}" state="false">{{ playlist['name'] }}</input>
    })
    buttons.forEach((instance) => {
        buttonContainer.appendChild(instance)
    })
};