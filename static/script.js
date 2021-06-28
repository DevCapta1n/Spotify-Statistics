const urlBase = "http://127.0.0.1:5000/";

function time_range(evt) {
    evt.preventDefault()

    let artist_range = $("#artist_time").val();
    let track_range = $("#track_time").val();

    const two_vals = [artist_range, track_range]
    let count = 0;
    for (val in two_vals) {
        console.log(two_vals[val])
        console.log(two_vals[val] == 'Six Months')
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

$("#time_form").on("submit", time_range);