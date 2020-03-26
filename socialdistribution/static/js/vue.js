// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    data: function() {
        return {
            posts: [],
            currentAuthor: {},
            mode: "posts"
        }
    },
    methods: {
        // Get posts visible to the currently authenticated user
        getPosts: function() {
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
        getCurrentAuthor: function() {
            const url = "/api/whoami";
            // get posts
            fetch(url)
                .then(response => response.json())
                .then(json => {
                    this.currentAuthor = json["author"];
                    console.log(this.currentAuthor);
                });        
        }
    },
    // runs when the vue app is created
    created() {
        this.getPosts();
        this.getCurrentAuthor();
    }
})