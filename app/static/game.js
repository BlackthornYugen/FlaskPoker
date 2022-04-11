function createPlayer(id) {
    // check if player already exists
    let playerRow = document.getElementById(id);

    if (playerRow) {
        return playerRow;
    }

    playerRow = document.createElement("tr");
    playerRow.id = id
    let nameData = document.createElement("td")
    let voteData = document.createElement("td")
    playerRow.appendChild(nameData);
    playerRow.appendChild(voteData);
    document.getElementsByTagName("tbody")[0].appendChild(playerRow);
    return playerRow;
}

window.onload = () => {
    const socket = io();
    socket.io.opts.transports = ["websocket"];
    let nameEvent = null;

    socket.on("vote", votes => {
        votes.forEach(vote => {
            let row = createPlayer(vote['user']);
            row.getElementsByTagName("td")[1].innerText = vote['value']
        })
        console.log(votes)
    });

    socket.on("name", message => {
        let row = createPlayer(message['id']);

        row.getElementsByTagName("td")[0].innerText = message['name']

        console.log(message)
    });

    const voteButtons = document.getElementById("vote").getElementsByTagName("button")
    for (let button of voteButtons) {
        button.onclick = click => {
            socket.emit('vote', {data: click.target.innerHTML});
            console.log(click.target.innerHTML)
            click.target
            for ( let button of voteButtons ) {
                button.classList.remove("me");
                click.target.classList.add("me");
            }
        }
    }

    document.getElementById("flipButton").onclick = () => {
        socket.emit('flip', {});
    }

    function changeName(event) {
        // change in 1 second
        clearTimeout(nameEvent);
        nameEvent = setTimeout((value) => {
            socket.emit('name', { data: value });
        }, 300, event.target.value)

    }

    document.getElementById("name").onchange = changeName;
    document.getElementById("name").onkeyup = changeName;
}