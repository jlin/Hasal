wait("chrome_urlbar-2.png")
paste("chrome_urlbar-1.png", "https://goo.gl/MVSoZo")
type(Key.ENTER)
setAutoWaitTimeout(10)
wait("1469424086910.png")
wheel("1469424086910.png", WHEEL_DOWN, 2)
paste("1469424086910.png", "https://www.mozilla.org")
wait("1468911047850.png")
click(Pattern("1468915035222.png").targetOffset(50,0))
