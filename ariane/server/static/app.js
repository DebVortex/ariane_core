$(document).ready(function() {
    $('#ariane-form').on('submit', function(e) {
        e.preventDefault()
        q = $('#query').val()
        language = $('#language').val()
        $.ajax({
            method: "POST",
            url: "/api",
            data: { q: q, language: language }
        }).done(function( msg ) {
            $('.output').fadeOut(1000, function() {
                $('.output').html(msg)
                $('.output').fadeIn()
            })
        });
    })
})
