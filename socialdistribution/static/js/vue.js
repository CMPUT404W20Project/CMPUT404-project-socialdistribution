// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    // data is an object which can be accessed in the HTML attributes
    data: function () {
        return {
            posts_url: "/api/posts",
            posts: []
        }
    },
    methods: {
        reloadPosts: function () {
            // get posts
            fetch(this.posts_url)
                .then(response => response.json())
                .then(json => {
                    this.posts = json["posts"];
                    console.log(this.posts);
                });
        }
    },
    // runs when the vue app is created
    created() {
        this.reloadPosts();
    }
})