// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    data: function () {
        return {
            post: null,
            currentAuthor: {},
            converter: null,
            editing: false
        }
    },
    methods: {
        // Get posts visible to the currently authenticated user
        getPost: function () {
            let postId = document.getElementById("post-id").value;

            const url = `/api/posts/${postId}`;

            // get post
            fetch(url)
                .then(response => response.json())
                .then(json => {
                    this.post = json["post"];
                });
        },
        // Get the currently authenticated user
        getCurrentAuthor: function () {
            const url = "/api/whoami";
            // get posts
            fetch(url)
                .then(response => response.json())
                .then(json => {
                    this.currentAuthor = json;
                });
        },
        deletePost: function(postId) {
            const url = `/api/posts/${postId}`;

            fetch(url, {
                method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
                mode: 'cors', // no-cors, *cors, same-origin
                cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
                credentials: 'same-origin', // include, *same-origin, omit
                redirect: 'follow', // manual, *follow, error
                referrerPolicy: 'no-referrer', // no-referrer, *client
            }).then((response) => {
                window.location.replace(`/stream`);
            });
        },
        commentOnPost: function(post) {
            const url = `${post.origin}/comments`;

            let commentInputId = `#comment-${post.id}`;
            // get comment text
            let commentText = document.querySelector(commentInputId).value;
            // clear textarea
            document.querySelector(commentInputId).value = "";
            // the actual comment
            let comment = {
                "query": "addComment",
                "post": post.id,
                "comment": {
                    "author": this.currentAuthor,
                    "comment": commentText,
                    "contentType": "text/plain",
                }
            }

            postJson(url, comment).then(
                (json) => {
                    this.getPost();
                });
        }
    },
    // runs when the vue app is created
    created() {
        this.converter = new showdown.Converter(),
        this.getPost();
        this.getCurrentAuthor();
    }
})