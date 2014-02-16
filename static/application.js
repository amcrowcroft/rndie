$(document).ready(function(){
  
    //Hide content on load
    $(".blog-body").hide(); 


    //Slide up and down on click
    $(".morebutton").click(function(){
      $(this).next(".blog-body").slideToggle("fast");
      });
 


});