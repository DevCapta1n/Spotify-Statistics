it('should replace the home page content with the appropriate four weeks data', async function() {
    let returned_html = undefined;
    $("#artist_time").val('Four Weeks').change();
    $("#track_time").val('Four Weeks').change();
    returned_html = await time_range();
    expect(returned_html).toContain('<h1>Your Top Artists For The last Four Weeks:</h1>')
    expect(returned_html).toContain('<h1>Your Top Tracks For The Last Four Weeks:</h1>')
})

it('should replace the home page content with the appropriate six months data', async function() {
    let returned_html = undefined;
    $("#artist_time").val('Six Months').change();
    $("#track_time").val('Six Months').change();
    returned_html = await time_range()
    expect(returned_html).toContain('<h1>Your Top Artists For The last Six Months:</h1>')
    expect(returned_html).toContain('<h1>Your Top Tracks For The Last Six Months:</h1>')
})

it('should replace the home page content with the appropriate all time data', async function() {
    let returned_html = undefined;
    $("#artist_time").val('All Time').change();
    $("#track_time").val('All Time').change();
    returned_html = await time_range()
    expect(returned_html).toContain('<h1>Your All Time Top Artists:</h1>')
    expect(returned_html).toContain('<h1>Your All Time Top Tracks:</h1>')
})