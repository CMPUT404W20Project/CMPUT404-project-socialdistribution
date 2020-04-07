// VueJS
var vm = new Vue({
    // HTML element
    el: "#vue-app",
    data: function () {
        return {
            posts: [],
            filteredPosts: [],
            currentAuthor: {},
            converter: null,
            postCategories: new Set(),
            filterCategories: new Set(),
            filterLocal: true,
            filterRemote: true
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
                    this.updateCategories();
                    this.filterPosts();
                });
        },
        updateCategories: function () {
            this.postCategories.clear();
            for (let post of this.posts) {
                for (let category of post.categories) {
                    this.postCategories.add(category);
                }
            }
            // workaround since vue does not support reactive Sets
            this.postCategories = new Set(this.postCategories);
        },
        filterPosts: function () {
            this.filteredPosts.clear();
            for (let post of this.posts) {
                // TODO
                if (this.filterLocal && true) {
                    this.filteredPosts.push(post);
                }
            }
        },
        toggleCategory: function (category) {
            if (this.filterCategories.has(category)) {
                this.filterCategories.delete(category);
            }
            else {
                this.filterCategories.add(category);
            }
            // workaround since vue does not support reactive Sets
            this.filterCategories = new Set(this.filterCategories);
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
                console.log(response);
                this.getPosts();
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
                    // console.log(json);
                    this.getPosts();
                });
        }
    },
    // runs when the vue app is created
    created() {
        this.converter = new showdown.Converter(),
        this.getPosts();
        this.getCurrentAuthor();
    }
})