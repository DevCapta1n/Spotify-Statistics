const urlBase = "http://127.0.0.1:5000/";
// function populate_stats() {
//     console.log(sessionStorage.getItem('test'));
// }

async function time_range(evt) {
    evt.preventDefault()

    console.log('checkpoint')
    console.log($("#artist_time").val())
    console.log($("#track_time").val())
    console.log($("#time_button").attr('name'))
    let artist_range = $("#artist_time").val();
    let track_range = $("#track_time").val();

    const two_vals = [artist_range, track_range]
    let count = 0;
    for (val in two_vals) {
        console.log(two_vals[val])
        console.log(two_vals[val] == 'Six Months')
        if (two_vals[val] == 'All Time') {
            if (count == 0) {
                artist_range = 'long_term'
                count = 1;
            } else {
                track_range = 'long_term'
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
                artist_range = 'short_term'
                count = 1;
            } else {
                track_range = 'short_term'
            }
        }
    }
    const user_id = $("#time_button").attr('name')
    const url = urlBase + 'statistics-home/' + user_id
    const data = {
        artist_range,
        track_range
    }
    //const alt_data = `${artist_range},${track_range}`
    const alt_data = {'artist_range': artist_range, 'track_range': track_range}
    // resp = await axios.post(url, data);
    // console.log(resp)
    // console.log(resp['data'])
    //console.log(resp['data'])
    // $("html").html(resp['data']);
    // $("body").css('background-color', 'cornsilk');
    // console.log($("body").css('background-color'))
    // console.log($("template").css('background-color'))
    // $("p").css('background-color', 'cornsilk');
    $("#stats_home").load(url, alt_data)
}

$("#time_form").on("submit", time_range);

//$( document ).ready( populate_stats )