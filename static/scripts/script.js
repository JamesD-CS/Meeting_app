
window.onload=function(){
	
	
	document.getElementById("time_zone").addEventListener("change", getName); 

	function getName(){
		var tz_name = document.getElementById("tz_name");
		var tz_selector = document.getElementById("time_zone");
		tz_text = tz_selector.options[tz_selector.selectedIndex].text;
		tz_name.value = tz_text;
	}	

	 
	 

}