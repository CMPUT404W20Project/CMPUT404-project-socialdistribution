/**
 * Displays the Github activities of the user
 * 
 * Append all Githb events at the bottom of all posts in the /stream
 * 
 */
var markup = '<div class="post-card" id="github-post">\
<!--start of the post heading-->\
<div class="post-heading">\
    <div class="post-author">\
        <div class="post-author-img">\
            <img src="${event.actor.avatar_url}"  alt="">\
        </div>\
        <div class="post-author-body">\
            <p class="post-author-name">GitHub Activity - ${event.actor.display_login}</p>\
            <p class="post-timestampe">${event.created_at}</p>\
        </div>\
    </div>\
</div>\
<!--end of the post heading-->\
<!--start of the post item-->\
<div class="post-item">\
    <h5 class="post-card-title">${event.type} on</h5>\
    <a class="post-card-text" href="https://github.com/${event.repo.name}">${event.repo.name}</a>\
    {{if event.type == "PullRequestEvent"}}\
    <p>${event.payload.pull_request.body}</p>\
    {{else event.type == "PullRequestReviewCommentEvent" }}\
    <p>${event.payload.comment.body}</p>\
    {{else event.type == "IssueCommentEvent" }}\
    <p><a href="${event.payload.comment.html_url}">detail</a></p>\
    {{else event.type == "IssuesEvent" }}\
    <p><a href="${event.payload.issue.html_url}">${event.payload.issue.title}</a></p>\
    {{/if}}\
</div>\
<!--end of the post item-->'


$(document).ready(function() {
    var authorId = $(".profile-header-info").attr("id");
    var githubName;
    $.template( "githubTemplate", markup );

    /**
     * Get the Github Account of the authenticated user,
     * and then make a Github API event request to get all the events
     * from the Github.
     */
    $.ajax({
        url: '/api/author/' + authorId,
        method: 'GET',
        success: function(result) {
            githubName = result.github.split("/")[3];
            githubName = githubName.toLowerCase();
        },
        error: function(request,msg,error) {
            console.log('fail to get user github');
        }
    }).done(function() {
        $.ajax({
            url: 'https://api.github.com/users/' + githubName + '/events',
            method: 'GET',
            success: function(events) {
                for (event of events) {
                    // console.log(event);
                    // console.log(event.created_at);
                    // console.log($(template_author).ready());
                    $.tmpl( "githubTemplate", event ).appendTo("#my-stream" );
                };
            },
            error: function(request,msg,error) {
                console.log('fail to get the the github stream');
            }
        });  
    }); 

    /**
     * Handle the filter for the post
     * 
     * Show all: Show all the posts.
     * Local: Show the local posts.
     * Remote: Show the remote posts.
     * My Posts: Show the posts that are belong to the author itself,
     *           and the posts included all visibility type.
     * Public: Show all the posts that are public.
     * Friend: Show all the posts from the frends of the author, and
     *         the post can be PRIVATE(but visible to this author), PUBLIC,
     *         FRIENDS, FOAF.
     * Github: Show the github stream. //TODO: Need treat the github activity as a post.
     */
    $("#all").addClass(" active");
    $("#all").focus();
    $(".btn").click(function(){
        $(".btn.active").removeClass(" active");
        $(this).addClass(" active");

        var type = $(this).attr("id");

        if (type === "all"){
            // console.log("all post");

            $('div[id^="non-github-post"]').show();

        }else if (type === "local"){
            console.log("local");
        }else if (type === "remote"){
            console.log("remote");
        }else if (type === "my_post"){
            console.log("my post");

            var authorId = $(".profile-header-info").attr("id");
            $('div[id^="non-github-post"]').show();

            $('div[id^="non-github-post"]').each(function(){
                var postAuthorId = $(this).find(".post-author").attr("id");
                if (postAuthorId !== authorId){
                    $(this).hide();
                }
            });

        }else if (type === "public"){
            $('div[id^="non-github-post"]').show();

            $('div[id^="non-github-post"]').each(function(){
                var postVsibility = $(this).attr("name");
                if (postVsibility !== "PUBLIC"){
                    $(this).hide();
                }
            });

        }else if (type === "friend"){
            //TODO: Currently get the post which is not belong to the author
            // We need set up constraints that the posts are only belong to
            // the friends of the author.
            console.log("friend");

            var authorId = $(".profile-header-info").attr("id");
            $('div[id^="non-github-post"]').show();

            $('div[id^="non-github-post"]').each(function(){
                var postAuthorId = $(this).find(".post-author").attr("id");
                if (postAuthorId === authorId){
                    $(this).hide();
                }
            });

        }else if (type === "github"){
            // console.log("github");

            $('div[id^="non-github-post"]').hide();
        }
    })
});
