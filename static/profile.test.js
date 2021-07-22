//a single test for the single profile page specific function
it('should contain the edit form after the edit_profile function runs', async function() {
    expect($('#right_profile_div').html()).toContain(`<button class="btn btn-lrg btn-warning" role="button">Edit</button>`)
    await edit_profile()
    expect($('#profile_content').html()).toContain(`<span>Leave any field to let it remain unchanged</span>`)
    expect($('#profile_content').html()).toContain(`<button class="btn btn-warning" role="button">Edit</button>`)
})