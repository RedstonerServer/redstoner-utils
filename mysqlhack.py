import java.lang.reflect.Method
import java.io.File
import java.net.URL
import java.net.URLClassLoader
import jarray
from java.lang import Class


# hacky code to add mysql-connector to java's classpath ('classPathHack')
jarfile = "lib/mysql-connector-java-5.1.14-bin.jar"
driver  = "com.mysql.jdbc.Driver"

url       = java.io.File(jarfile).toURL()
sysloader = java.lang.ClassLoader.getSystemClassLoader()
sysclass  = java.net.URLClassLoader
method    = sysclass.getDeclaredMethod("addURL", [java.net.URL])

method.setAccessible(1)
jarray.array([url], java.lang.Object)
method.invoke(sysloader, [url])
Class.forName(driver)
