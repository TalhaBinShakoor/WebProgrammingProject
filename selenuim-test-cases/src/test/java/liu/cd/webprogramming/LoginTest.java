package liu.cd.webprogramming;

import static org.junit.Assert.*;

import java.sql.Driver;
import java.util.Date;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;
import org.openqa.selenium.By;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class LoginTest {

	static  WebDriver driver; /*= driver = new ChromeDriver();*/

	@BeforeClass
	public  static  void setup() {
//		String path = System.getProperty("/home/mutaz");
		System.setProperty("webdriver.chrome.driver", "D:\\New folder\\chromedriver.exe");
		driver = new ChromeDriver();
		driver.manage().window().maximize();
		driver.get("http://twidder7-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/");
	}

	@Test
	public void test1Signup() throws InterruptedException {
		System.out.println("testing signup start");
		//initWebDriver("http://twwider2-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/");
		driver.findElement(By.xpath("//input[@id='signup-firstname']")).sendKeys("Mutaz");
		driver.findElement(By.xpath("//input[@id='signup-familyname']")).sendKeys("Kabashi");
		// driver.findElement(By.xpath("//input[@id='signup-gender']")).sendKeys("Male");
		/*
		 * WebElement element=driver.findElement(By.id("signup-gender")); WebDriverWait
		 * wait = new WebDriverWait(driver,30);
		 * wait.until(ExpectedConditions.visibilityOf(element));
		 */
		Select drpGender = new Select(driver.findElement(By.name("signupGender")));
		drpGender.selectByValue("male");
		driver.findElement(By.xpath("//input[@id='signup-city']")).sendKeys("Khartoum");
		driver.findElement(By.xpath("//input[@id='signup-country']")).sendKeys("Sudan");
		driver.findElement(By.xpath("//input[@id='signup-telephone']")).sendKeys("46764449643");
		driver.findElement(By.xpath("//input[@id='signup-email']")).sendKeys("mutaz1234@abc.com");
		driver.findElement(By.xpath("//input[@id='signup-password']")).sendKeys("1234567890");
		driver.findElement(By.xpath("//input[@id='signup-repeatpassword']")).sendKeys("1234567890");
		driver.findElement(By.xpath("//input[@id='signupBtn']")).click();
		// wait(1000);
		// WebElement e
		// =driver.findElement(By.xpath("//input[@id='signup-errorMessage']"));
		WebElement element = driver.findElement(By.id("signup-errorMessage"));
		WebDriverWait wait = new WebDriverWait(driver, 30);
		wait.until(ExpectedConditions.visibilityOf(element));
		System.out.println("message " + element.getText());
		assertTrue(element.getText().equals("Successfully created a new user."));

	}

	@Test
	public void test2SignIn() throws InterruptedException {
		System.out.println("testing SignIn start");
		//initWebDriver("http://twwider2-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/");
		driver.findElement(By.xpath("//input[@id='login-email']")).sendKeys("mutaz1234@abc.com");
		driver.findElement(By.xpath("//input[@id='login-password']")).sendKeys("1234567890");
		driver.findElement(By.xpath("//input[@id='loginBtn']")).click();
		// WebElement element=driver.findElement(By.id("signin-errorMessage"));
		WebElement pageContentElement = driver.findElement(By.id("page-content"));
		WebDriverWait wait = new WebDriverWait(driver, 30);
		wait.until(ExpectedConditions.invisibilityOf(driver.findElement(By.xpath("//input[@id='login-email']"))));
		// pageContentElement.getAttribute("innerHTML").contains("User Information")
		// WebElement pageContentElement=driver.findElement(By.id("page-content"));
		//System.out.println("message " + pageContentElement.getText());// page-content
		assertTrue(pageContentElement.getAttribute("innerHTML").contains("User Information"));

	}
	
	
	  @Test public void test3PostMessageSuccess() throws InterruptedException {
	  System.out.println("testing PostMessage start"); 
	  //initWebDriver("http://twwider2-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/");
	  String post = "today is "+new Date();
	  driver.findElement(By.name("homePostText")).sendKeys(post);
	  driver.findElement(By.xpath("//input[@id='home_post_Button']")).click();
	  WebDriverWait wait = new WebDriverWait(driver, 30);
	  wait.until(ExpectedConditions.textToBePresentInElementValue(By.name(
	  "homePostText"), post));
	  
	  }
	  
	  @Test public void test4LogOut() throws InterruptedException {
	  System.out.println("testing Logout start"); 
	  //initWebDriver("http://twwider2-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/");
	  driver.findElement(By.xpath("//input[@id='home_logout']")).click();
	  WebElement pageContentElement = driver.findElement(By.id("page-content"));
	  WebDriverWait wait = new WebDriverWait(driver, 30);
	  wait.until(ExpectedConditions.invisibilityOf(driver.findElement(By.xpath("//input[@id='home_logout']"))));
	  assertTrue(pageContentElement.getAttribute("innerHTML").
	  contains("Forget password"));
	  
	  }
	  
	  @Test
	  public void test5ForgetPassword() throws InterruptedException {
	  System.out.println("testing ForgetPassword start");
	  //String forgetPasswordMessage = "New Password Generated successfully, sms has been sent to you with the new password";
	  //initWebDriver("http://twwider2-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/forgetPassword.html");
	  driver.get("http://twidder7-mutab736-dev.apps.sandbox.x8i5.p1.openshiftapps.com/forgetPassword.html");
	  driver.findElement(By.xpath("//input[@id='forgetpassword-email']")).sendKeys("mutaz1234@abc.com");
	  driver.findElement(By.xpath("//input[@id='forgetpassword-Btn']")).click();
	  //WebElement pageContentElement = driver.findElement(By.id("forgetpassword-errorMessage"));
	  By byXpath = By.xpath("//*[contains(text(),'New Password Generated successfully, sms has been sent to you with the new password')]");
	  WebDriverWait wait = new WebDriverWait(driver, 30);
	  wait.until(ExpectedConditions.presenceOfElementLocated(byXpath)); 
	  
	  }
	 
	
	//util Methods
	/*
	 * public void initWebDriver(String url) { driver = new ChromeDriver();
	 * driver.manage().window().maximize(); driver.get(url); }
	 */
	

}
