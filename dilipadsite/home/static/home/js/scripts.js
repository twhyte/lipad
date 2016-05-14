$(document).mouseup(function (e)
{
    var container = $(".portfolio-item");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
			$(".portfolio-item").removeClass( "open" );
			$(".portfolio-item").removeClass( "fade" );
    }
});

$( document ).ready(function() {
 
  $( ".nav-button" ).click(function() {
 		$( this ).toggleClass( "open" );
		$( ".main-nav" ).toggleClass( "open" );
	});

	$(".main-nav li").click(function () {
		$( ".nav-button" ).removeClass( "open" );
		$( ".main-nav" ).removeClass( "open" );
	});


	$( ".portfolio-item" ).click(function() {
		if ($(this).hasClass('open')) {
			$(".open .img-cont").outerHeight("");
			$(".portfolio-item").removeClass( "open" );
			$(".portfolio-item").removeClass( "fade" );
		} else {
			$(".portfolio-item").not( this ).removeClass( "open" );
			$( this ).removeClass( "fade" );
			$(".portfolio-item").not( this ).addClass( "fade" );
			$( this ).toggleClass( "open" );
		};
	});
		 
	equalHeight();
	scollOpacity(); 

	$(window).scroll(function() {  
	    parallaxScroll();  
	    scollOpacity(); 
	    stickyNav();  
	});  

	$(window).resize(function() {  
		equalHeight();
	});  

	$(window).load(function() {
		equalHeight();
		resizeBg();
	});

	var theWindow        = $(window),
	  $bg              = $("#bg img"),
	  aspectRatio      = $bg.width() / $bg.height();
	  			    		
	function resizeBg() {

		if ( (theWindow.width() / theWindow.height()) < aspectRatio ) {
		    $bg
		    	.removeClass()
		    	.addClass('bgheight');
		} else {
		    $bg
		    	.removeClass()
		    	.addClass('bgwidth');
		}
					
	};
	                 			
	theWindow.resize(resizeBg).trigger("resize");

	function equalHeight(){

		$(".plan").height('auto')

		var maxHeight = 0;

		$(".plan").each(function(){
		   if ($(this).height() > maxHeight) { maxHeight = $(this).height(); }
		});

		$(".plan").height(maxHeight);

	};

	function scollOpacity(){
		var scroll = $(window).scrollTop();
		var position = $('.scroll-opacity').offset().top; 
		var opacity = 1.25 - (1*(scroll / position));
		$('.scroll-opacity').css("opacity",opacity);
	};  

	function parallaxScroll(){
		var scrolled = $(window).scrollTop();
		$(".para-xs").css({transform: 'translateY(' + (scrolled / 4) + 'px)'});
		$(".para-sml").css({transform: 'translateY(' + (scrolled / 3) + 'px)'});
		$(".para-med").css({transform: 'translateY(' + (scrolled / 2) + 'px)'});
		$(".para-lrg").css({transform: 'translateY(' + (scrolled / 1.5) + 'px)'});
		$(".para-xl").css({transform: 'translateY(' + (scrolled / 1.2) + 'px)'});
	};

	var stickyNavTop = $('#header').offset().top;  
	function stickyNav(){
		var scrollTop = $(window).scrollTop() - ($( window ).height() / 1.5);     
		if (scrollTop > stickyNavTop) {   
		    $('#header').addClass('fixed');  
		} else {  
		    $('#header').removeClass('fixed');   
		};
	};  

	$('a[href^="#"]').on('click',function (e) {
	    e.preventDefault();
	    var target = this.hash;
	    $target = $(target);
	    $('html, body').stop().animate({
	        'scrollTop': $target.offset().top - 60
	    }, 900, 'swing', function () {
	        //window.location.hash = target;
	    });
	});

	var autoAdvance = 1;
	var timer = undefined;
	timer = setInterval(function(){
		if (autoAdvance == 1){
			if ($('.image-slider').is(':hover')) {
				return;
			} else {
				sliderForward();
			}
	  } else {
	  	setTimeout(function(){autoAdvance = 1;}, 8000); 
	  };
	}, 8000);
	$('.image-slider .wrapper .column-12').append($('.image-slider .wrapper .column-12').children().clone());    

	$( ".image-slider .right" ).click(function(event) {
		event.preventDefault();
		sliderForward();
		autoAdvance = 0;
		var btn = $(this);
	  btn.prop('disabled',true);
	  window.setTimeout(function(){ 
	      btn.prop('disabled',false);
	  },500);
	});
	$( ".image-slider .left" ).click(function(event) {
		event.preventDefault();
		sliderBackward();
		autoAdvance = 0;
		var btn = $(this);
	  btn.prop('disabled',true);
	  window.setTimeout(function(){ 
	      btn.prop('disabled',false);
	  },500);
	});
	function sliderForward(){
		$('.image-slider .slide:first-child').insertAfter(".image-slider .slide:last-child");
	};
	function sliderBackward(){
		$('.image-slider .slide:last-child').insertBefore(".image-slider .slide:first-child");
	};

	var autoAdvanceTestimonial = 1;
	var timerTestimonial = undefined;
	timerTestimonial = setInterval(function(){
		if (autoAdvanceTestimonial == 1){
			sliderForwardTestimonial();
	  } else {
	  	setTimeout(function(){autoAdvanceTestimonial = 1;}, 8000); 
	  };
	}, 8000);
	$('.testimonial-slider .wrapper .column-12').append($('.testimonial-slider .wrapper .column-12').children().clone());    

	$( ".testimonial-slider .right" ).click(function(event) {
		event.preventDefault();
		sliderForwardTestimonial();
		autoAdvanceTestimonial = 0;
		var btn = $(this);
	  btn.prop('disabled',true);
	  window.setTimeout(function(){ 
	      btn.prop('disabled',false);
	  },500);
	});
	$( ".testimonial-slider .left" ).click(function(event) {
		event.preventDefault();
		sliderBackwardTestimonial();
		autoAdvanceTestimonial = 0;
		var btn = $(this);
	  btn.prop('disabled',true);
	  window.setTimeout(function(){ 
	      btn.prop('disabled',false);
	  },500);
	});
	function sliderForwardTestimonial(){
		$('.testimonial-slider .slide:first-child').insertAfter(".testimonial-slider .slide:last-child");
	};
	function sliderBackwardTestimonial(){
		$('.testimonial-slider .slide:last-child').insertBefore(".testimonial-slider .slide:first-child");
	};

	$('.portfolio').magnificPopup({
		delegate: 'a',
		type: 'image',
		tLoading: 'Loading image #%curr%...',
		mainClass: 'mfp-img-mobile',
		gallery: {
			enabled: true,
			navigateByImgClick: true,
			preload: [0,1] // Will preload 0 - before current, and 1 after the current image
		},
		image: {
			tError: '<a href="%url%">The image #%curr%</a> could not be loaded.',
			titleSrc: function(item) {
				return item.el.attr('title');
			}
		}
	});

});

