$(document).ready(function() {

    $("form#contact-form").submit(function(e) {

        var mydata = $("form#contact-form").serialize();
        console.log(mydata);
        $.ajax({
            type: "POST",
            url: "contactengine.php",
            data: mydata,
            success: function(response, textStatus, xhr) {
                $("#contact-form  input[required=true], #contact_form textarea[required=true]").val(''); 
                $("#contact-form #contact-body").slideUp(); //hide form after success
                $("#contact-form #success").slideDown(); //show success message
            },
            error: function(xhr, textStatus, errorThrown) {
                //Place code here if you'd like something to happen if the form doesn't go through.
            }
        });
        return false;

    });

});

