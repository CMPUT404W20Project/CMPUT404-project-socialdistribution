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

// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    data: function () {
        return {
            posts: [],
            currentAuthor: {},
            mode: "posts",
            focusPost: null
        }
    },
    methods: {
        // Get posts visible to the currently authenticated user
        getPosts: function () {
            const url = "/api/author/posts";
            // get posts
            fetch(url)
                .then(response => response.json())
                .then(json => {
                    this.posts = json["posts"];
                    console.log(this.posts);
                });
        },
        // Get the currently authenticated user
        getCurrentAuthor: function () {
            const url = "/api/whoami";
            // get posts
            fetch(url)
                .then(response => response.json())
                .then(json => {
                    this.currentAuthor = json["author"];
                    console.log(this.currentAuthor);
                });
        },
        nameForAuthor: function (author) {
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
        },
        // parse ISO8601 date and make it nice
        prettyDate(date) {
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
        },
        deletePost(postId) {
            const url = `/api/posts/${postId}`;

            fetch(url, {
                method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
                mode: 'cors', // no-cors, *cors, same-origin
                cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
                credentials: 'same-origin', // include, *same-origin, omit
                redirect: 'follow', // manual, *follow, error
                referrerPolicy: 'no-referrer', // no-referrer, *client
            }).then((response) => {
                console.log(response);
                this.getPosts();
            });
        },
        viewPost(post) {
            this.focusPost = post;
            this.mode = "viewpost";
        },
        commentOnPost(postId) {
            const url = `/api/posts/${postId}/comments`;

            let commentInputId = `#comment-${postId}`;
            // get comment text
            let commentText = document.querySelector(commentInputId).value;
            // clear textarea
            document.querySelector(commentInputId).value = "";
            // the actual comment
            let comment = {
                "query": "addComment",
                "post": postId,
                "comment": {
                    "author": this.currentAuthor,
                    "comment": commentText,
                    "contentType": "text/plain",
                }
            }

            postJson(url, comment).then(
                (json) => {
                    console.log(json);
                    this.getPosts();
                });
        }
    },
    // runs when the vue app is created
    created() {
        this.getPosts();
        this.getCurrentAuthor();
    }
})