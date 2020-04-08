// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    data: function () {
        return {
            currentAuthor: {},
            profileAuthor: {},
            editing: false
        }
    },
    methods: {
        // Get the currently authenticated user
        getCurrentAuthor: function () {
            const url = "/api/whoami";
            // get posts
            fetch(url)
                .then(response => response.json())
                .then(json => {
                    this.currentAuthor = json["author"];
                });
        },
        addFriend: function() {
            const url = `/api/friendrequest`;

            let postBody = {
                "query": "friendrequest",
                "author": this.currentAuthor,
                "friend": this.profileAuthor
            }

            console.log(postBody);

            postJson(url, postBody).then(
                (json) => {
                    console.log(json);
                });
        },
        deleteFriend: function(){
            const url = `${this.profileAuthor.host}/api/friendrequest`;

            fetch(url, {
                method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
                mode: 'cors', // no-cors, *cors, same-origin
                cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
                credentials: 'same-origin', // include, *same-origin, omit
                redirect: 'follow', // manual, *follow, error
                referrerPolicy: 'no-referrer', // no-referrer, *client
            }).then((response) => {
                console.log(response);
                window.location.reload();
            });
        }
    },
    // runs when the vue app is created
    created() {
        let authorId = document.getElementById("user-id").value;
        getAuthor(authorId).then((author) => this.profileAuthor = author);

        this.getCurrentAuthor();
    }
})
