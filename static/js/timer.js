function startCountdown(timeInSeconds, onTimeUp) {
  let timeLeftSpan = document.getElementById("timeLeft");
  let interval = setInterval(() => {
    if(timeInSeconds <= 0) {
      clearInterval(interval);
      timeLeftSpan.innerHTML = "Süre Doldu!";
      if(onTimeUp) {
        onTimeUp();
      }
      return;
    }
    timeLeftSpan.innerHTML = timeInSeconds;
    timeInSeconds--;
  }, 1000);
}
