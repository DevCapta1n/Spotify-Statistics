it('should return a random number', function() {
    expect(typeof(getRandomInt(4567))).toEqual('number')
})

it('should display a random background image', function() {
    backGroundImage()
    expect($("body").css('background-image')).toContain('url("http://127.0.0.1:5000/static/images/')
})

it('should display the time of last modification', function() {
    const dateObject = new Date(document.lastModified);

    const month = dateObject.getUTCMonth() + 1;
    const day = dateObject.getUTCDate();
    const year = dateObject.getUTCFullYear();
    const calendarDate = `${month}/${day}/${year}`
    expect($("#modified").html()).toContain("last updated: " + calendarDate)
})

it('should hide content and display the loading spinner', function() {
    expect($('.loader').css('display')).toEqual('none')
    loading()
    expect($('#content-wrap').css('display')).toEqual('none')
    expect($('.loader').css('display')).toEqual('block')
})