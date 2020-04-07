// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    data: function () {
        return {
            currentAuthor: {},
            profileAuthor: {}
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
                    this.currentAuthor = json;
                });
        },
        addFriend: function() {
            const url = `${this.profileAuthor.host}/api/friendrequest`;

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
        }
    },
    // runs when the vue app is created
    created() {
        let authorId = document.getElementById("user-id").value;
        getAuthor(authorId).then((author) => this.profileAuthor = author);

        this.getCurrentAuthor();
    }
})