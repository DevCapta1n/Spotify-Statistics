//Javascript for Statify 
const urlBase = "https://statify-winford.herokuapp.com/";

async function time_range(evt) {
    /**
     * This function is triggered on the submission of the time form
     * on the home page.
     * It makes a call to the server and replaces the stats home area
     * of the page with the response html from the server.
     */
    if (evt != undefined) {
        //evt will be undefined in the case of this function being called
        //by a Jasmine test.
        evt.preventDefault()
    }

    let artist_range = $("#artist_time").val();
    let track_range = $("#track_time").val();

    const two_vals = [artist_range, track_range]
    let count = 0;
    for (const val in two_vals) {
        if (two_vals[val] == 'Four Weeks') {
            if (count == 0) {
                artist_range = 'short_term'
                count = 1;
            } else {
                track_range = 'short_term'
            }
        } else if (two_vals[val] == 'Six Months') {
            if (count == 0) {
                artist_range = 'medium_term'
                count = 1;
            } else {
                track_range = 'medium_term'
            }
        } else {
            if (count == 0) {
                artist_range = 'long_term'
                count = 1;
            } else {
                track_range = 'long_term'
            }
        }
    }

    const url = urlBase + 'statistics-home';
    const data = {'artist_range': artist_range, 'track_range': track_range};
    let stats = await axios.post(url, data);
    stats = stats.data;
    //readjust css properties to hide the loading spinner and show the
    //statistics content
    $('.loader').css('display','none')
    $("#stats_home").css('display', 'block')
    $('#home_footer').css('display','block')
    $("#stats_home").html(stats);
    return stats;
}

function lastModified() {
    /**
     * Function to dynamically update the footer with the date
     * of latest modifications.
     */
    const dateObject = new Date(document.lastModified);

    const month = dateObject.getUTCMonth() + 1;
    const day = dateObject.getUTCDate();
    const year = dateObject.getUTCFullYear();
    const calendarDate = `${month}/${day}/${year}`

    $("#modified").html("last updated: " + calendarDate);
}

function getRandomInt(max) {
    /**
     * Get a random int between 0 and max with zero inclusive but
     * max being exclusive.
     */
    return Math.floor(Math.random() * max);
}

function backGroundImage() {
    /**
     * Select one of three background images and set that image as the background
     * of the page body. (Credits for images in README.md)
     */
    if ($("#auth_body").length) {
        const randomInt = getRandomInt(3);

        if (randomInt == 0) {
            $("body").css('background-image', 'url(/static/images/travis-yewell-F-B7kWlkxDQ-unsplash.jpg)')
        } else if (randomInt == 1) {
            $("body").css('background-image', 'url(/static/images/mick-haupt-vGXHIh3URzc-unsplash.jpg)')
        } else if (randomInt == 2) {
            $("body").css('background-image', 'url(/static/images/heidi-fin-H4fYXZ1hyco-unsplash.jpg)')
        }
    }
}

function loading() {
    $('.loader').next().css('display','none')
    if ($('#auth_footer').length) {
        $('#auth_footer').css('display','none')
    } else if ($('#home_footer').length) {
        $('#home_footer').css('display','none')
    }
    $('.loader').css('display','block')
}

$('#profile_form').on("submit", async function(evt) {
    evt.preventDefault()
    let user = await axios.get('https://statify-winford.herokuapp.com/get-user')
    user = user.data
    $('#profile_content').html(`
    <form action="/profile" method="POST">
    <div>
        <div class="form_element">
            <span>Leave any field to let it remain unchanged</span>
        </div>
        <div class="form_element form-group">
            <label for="picture">an URL of any image</label>
            <input class="form-control short_input" name="picture" type="text" value="${user.profile_pic_url}">
        </div>
        <div class="form_element form-group">
            <label for="username">display name</label>
            <input class="skinny form-control" name="username" type="text" maxlength="30" value="${user.display_name}">
            <small id="passwordHelpBlock" class="form-text text-muted">
                Limit of thirty characters
            </small>
        </div>
        <div class="form_element form-group" id="countriesList">

        </div>
        <div class="form_element">
            <button class="btn btn-warning" role="button">Edit</button>
        </div>
    </div>
    </form>
    `)
    $(document).ready(function() {
        $('#countriesList').load('/country-drop-down');
    });
});
//if the auth_body id exists then the page must be the authorization page
backGroundImage();

lastModified();

$("#time_form").on("submit", loading)
$("#time_form").on("submit", time_range);

$('.auth_form').on("submit", loading)

$('#profile_form').on('submit', edit_profile);