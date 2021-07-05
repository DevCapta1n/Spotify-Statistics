//Javascript for Statify 
const urlBase = "http://127.0.0.1:5000/";

function time_range(evt) {
    /**
     * This function is triggered on the submission of the time form
     * on the home page.
     * It makes a call to the server and replaces the stats home area
     * of the page with the response html from the server.
     */
    evt.preventDefault()

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
    const user_id = $("#time_button").attr('name')
    const url = urlBase + 'statistics-home/' + user_id

    const data = {'artist_range': artist_range, 'track_range': track_range}

    $("#stats_home").load(url, data)
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
    const randomInt = getRandomInt(3);

    if (randomInt == 0) {
        $("body").css('background-image', 'url(/static/images/travis-yewell-F-B7kWlkxDQ-unsplash.jpg)')
    } else if (randomInt == 1) {
        $("body").css('background-image', 'url(/static/images/mick-haupt-vGXHIh3URzc-unsplash.jpg)')
    } else if (randomInt == 2) {
        $("body").css('background-image', 'url(/static/images/heidi-fin-H4fYXZ1hyco-unsplash.jpg)')
    }
    
}

if ($("#auth_body").length) {
    //if the auth_body id exists then the page must be the authorization page
    backGroundImage()
}

lastModified()

$("#time_form").on("submit", time_range);

$('#auth_form').on("submit", function() {
    $('#content-wrap').css('display','none')
    $('#auth_footer').css('display','none')
    $('.loader').css('display','block')
    $('#auth_body').css('display','flex')
    $('#auth_body').css('justify-content','center')
    $('#auth_body').css('align-items','center')
})