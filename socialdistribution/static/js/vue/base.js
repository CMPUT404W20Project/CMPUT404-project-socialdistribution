// From: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
async function postJson(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *client
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return await response.json(); // parses JSON response into native JavaScript objects
}

function viewPost(post) {
    window.location.replace(`/stream/${post.id}`);
}

function editPost(post) {
    window.location.replace(`/stream/${post.id}/edit`);
}

function viewAuthor(author) {
    window.location.replace(`${author.url}/profile`);
}

function urlForAuthor(author) {
    return `${author.url}/profile`;
}

function nameForAuthor(author) {
    let keys = Object.keys(author);

    if (keys.includes("firstName") && keys.includes("lastName")) {
        return `${author.firstName} ${author.lastName}`;
    }
    else if (keys.includes("displayName") && author.displayName.length > 0) {
        return author.displayName;
    }
    else if (keys.includes("email")) {
        return author.email;
    }
    else {
        return author.id;
    }
}

// parse ISO8601 date and make it nice
function prettyDate(date) {
    try {
        let dateObj = Date.parse(date);
        return dateObj.toString();
    }
    catch(error) {
        const regexp = /(.*)\..*(\+.*)/g;
        try {
            let match = regexp.exec(date);
            let dateObj = Date.parse(`${match[1]}${match[2]}`);
            return dateObj.toString();
        }
        catch(error) {
            return date;
        }
    }
}

// Get the currently authenticated user
function getAuthor(authorId) {
    const url = `/api/author/${authorId}`;
    // get posts
    return fetch(url).then(response => response.json());
}