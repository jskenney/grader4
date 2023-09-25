#!/usr/bin/env bash

### Script to make a fake mvn project for the sole purpose
### of downloading dependencies.
### Designed for SI413 Fall 2023 by Dan Roche

tdir=$(mktemp -d makem2.XXXXXXXXXX)
cd "$tdir"

cat >pom.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>makem2</groupId>
  <artifactId>makem2</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>jar</packaging>

  <name>makem2</name>
  <description>Dummy project to get mvn dependencies downloaded.</description>
  <url>http://roche.work/</url>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <dependency>
      <groupId>org.antlr</groupId>
      <artifactId>antlr4-runtime</artifactId>
      <version>4.13.1</version>
    </dependency>
    <dependency>
      <groupId>org.antlr</groupId>
      <artifactId>antlr4</artifactId>
      <version>4.13.1</version>
    </dependency>
    <dependency>
        <groupId>net.harawata</groupId>
        <artifactId>appdirs</artifactId>
        <version>1.2.2</version>
    </dependency>
    <dependency>
      <groupId>org.jline</groupId>
      <artifactId>jline</artifactId>
      <version>3.23.0</version>
    </dependency>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
	<groupId>org.junit.platform</groupId>
	<artifactId>junit-platform-launcher</artifactId>
	<version>1.10.0</version>
	<scope>test</scope>
    </dependency>
    <dependency>
      <groupId>net.sourceforge.argparse4j</groupId>
      <artifactId>argparse4j</artifactId>
      <version>0.9.0</version>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.antlr</groupId>
        <artifactId>antlr4-maven-plugin</artifactId>
        <version>4.13.1</version>
        <executions>
          <execution>
            <id>antlr</id>
            <goals>
              <goal>antlr4</goal>
            </goals>
            <configuration>
              <visitor>true</visitor>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
	<artifactId>maven-compiler-plugin</artifactId>
        <version>3.11.0</version>
        <configuration>
          <release>17</release>
          <showDeprecation>true</showDeprecation>
          <!--<failOnWarning>true</failOnWarning>-->
          <compilerArgs>
            <arg>-Xlint:all</arg>
            <arg>-Xmaxerrs</arg>
            <arg>3</arg>
            <arg>-Xmaxwarns</arg>
            <arg>3</arg>
          </compilerArgs>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.1.0</version>
        <executions>
          <execution>
            <id>yes</id>
            <configuration>
              <mainClass>makem2.Yes</mainClass>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
	<artifactId>maven-clean-plugin</artifactId>
	<version>3.3.1</version>
      </plugin>
      <plugin>
	<artifactId>maven-surefire-plugin</artifactId>
	<version>3.1.2</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-shade-plugin</artifactId>
        <version>3.5.0</version>
        <executions>
          <execution>
            <phase>package</phase>
            <goals>
              <goal>shade</goal>
            </goals>
            <configuration>
              <transformers>
                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                  <manifestEntries>
                    <Main-Class>makem2.Yes</Main-Class>
                  </manifestEntries>
                </transformer>
              </transformers>
              <filters>
                <filter>
                  <artifact>*</artifact>
                  <excludes>
                    <exclude>META-INF/*</exclude>
                  </excludes>
                </filter>
              </filters>
            </configuration>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
EOF

mkdir -p "src/main/java/makem2"
cat >"src/main/java/makem2/Yes.java" <<'EOF'
package makem2;
public class Yes {
    public static void main(String[] args) { }
}
EOF

mkdir -p "src/main/antlr4/makem2"
cat >"src/main/antlr4/makem2/Gram.g4" <<'EOF'
grammar Gram;
stmt : NUM ;
NUM     : [0-9]+ ;
EOF

mkdir -p "src/test/java/makem2"
cat >"src/test/java/makem2/TestYes.java" <<'EOF'
package makem2;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.concurrent.TimeUnit;
@Timeout(value = 300, unit = TimeUnit.MILLISECONDS, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
public class TestYes {
    @Test
    void ok() {
        assertNotNull(new Yes(), "of course");
    }
}
EOF

mvn clean compile test-compile test exec:java@yes package dependency:resolve-plugins dependency:go-offline

cd
rm -rf "$tdir"

:
