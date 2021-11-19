<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html"/>

<xsl:template match="/">
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template name="verteiler">
  <xsl:for-each select="child::node()">
    <xsl:variable name="type">
      <xsl:apply-templates mode="detect-type" select="."/>
    </xsl:variable>
    <xsl:choose> 
      <xsl:when test="name()='at_command'">
        <xsl:call-template name="at_command"/> 
      </xsl:when>
      <xsl:when test="name()='atc_spec'">
        <xsl:call-template name="atc_spec"/> 
      </xsl:when>
      <xsl:when test="name()='subsubsection'">
        <xsl:call-template name="subsubsection"/> 
      </xsl:when>
      <xsl:when test="name()='descr'">
        <xsl:call-template name="descr"/>
      </xsl:when>
      <xsl:when test="name()='paramlist'">
        <xsl:call-template name="paramlist"/> 
      </xsl:when>
      <xsl:when test="name()='param'">
        <xsl:call-template name="param"/> 
      </xsl:when>
      <xsl:when test="name()='rc_code'">
        <xsl:call-template name="rc_code"/> 
      </xsl:when>
      <xsl:when test="name()='line'">
        <xsl:call-template name="line"/> 
      </xsl:when>
      <xsl:when test="name()='more'">
        ... 
      </xsl:when>
      <xsl:when test="name()='lref'">
        <xsl:call-template name="lref"/> 
      </xsl:when>
      <xsl:when test="name()='tref'">
        <xsl:call-template name="tref"/> 
      </xsl:when>
      <xsl:when test="name()='cref'">
        <xsl:call-template name="cref"/> 
      </xsl:when>
      <xsl:when test="name()='atcref'">
        <xsl:call-template name="atcref"/> 
      </xsl:when>
      <xsl:when test="name()='sref'">
        <xsl:call-template name="sref"/> 
      </xsl:when>
      <xsl:when test="name()='ssref'">
        <xsl:call-template name="ssref"/> 
      </xsl:when>
      <xsl:when test="name()='pref'">
        <xsl:call-template name="pref"/> 
      </xsl:when>
      <xsl:when test="name()='img_ref'">
        <xsl:call-template name="img_ref"/> 
      </xsl:when>
      <xsl:when test="name()='uref'">
        <xsl:call-template name="uref"/> 
      </xsl:when>
      <xsl:when test="name()='iref'">
        <xsl:call-template name="iref"/> 
      </xsl:when>
      <xsl:when test="name()='tabref'">
        <xsl:call-template name="tabref"/> 
      </xsl:when>
      <xsl:when test="name()='liref'">
        <xsl:call-template name="liref"/>
      </xsl:when>
      <xsl:when test="name()='code'">
        <xsl:call-template name="code"/> 
      </xsl:when>
      <xsl:when test="name()='ul'">
        <xsl:call-template name="list"/> 
      </xsl:when>
      <xsl:when test="name()='ol'">
        <xsl:call-template name="num_list"/> 
      </xsl:when>
      <xsl:when test="name()='table'">
        <xsl:call-template name="table"/> 
      </xsl:when>
      <xsl:when test="name()='br'">
        <br/>
      </xsl:when>
      <xsl:when test="name()='em'">
        <b><xsl:call-template name="verteiler"/></b>
      </xsl:when>
      <xsl:when test="name()='a'">&lt;a name='<xsl:value-of select="./@name"/>' href='<xsl:value-of select="./@href"/>'&gt;<xsl:call-template name="verteiler"/>&lt;/a&gt;</xsl:when>
      <!-- URCs ausgeben --> 
      <xsl:when test="name()='urc'">
        <xsl:call-template name="urc2"/>
      </xsl:when>
      <!-- parameter description ausgeben -->
      <xsl:when test="name()='pdescriptions'">
        <H2>Parameters:</H2>
        <xsl:call-template name="pdescriptions"/>
      </xsl:when>
      <xsl:when test="name()='center'">
        <div align="center">
        <xsl:call-template name="verteiler"/>
        </div>
      </xsl:when>
      <xsl:when test="name()='sup'">
        <xsl:call-template name="sup"/> 
      </xsl:when>
      <xsl:when test="name()='sub'">
        <xsl:call-template name="sub"/> 
      </xsl:when>
      <xsl:when test="name()='sp'">
        <font color="#FFFFFF">_</font>
      </xsl:when>
      <xsl:when test="name()='cr'">
        <tt>&lt;CR&gt;</tt>
      </xsl:when>
      <xsl:when test="name()='lf'">
        <tt>&lt;LF&gt;</tt>
      </xsl:when>
      <xsl:when test="name()='ctrlz'">
        <tt>&lt;Ctrl-Z&gt;</tt>
      </xsl:when>
      <xsl:when test="name()='esc'">
        <tt>&lt;ESC&gt;</tt>
      </xsl:when>
      <xsl:when test="name()='ie'">
        <!-- do nothing -->
      </xsl:when>
      <xsl:when test="name()='img'">
        <br/>
        <p align="center">
        &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
        &lt;img id='<xsl:value-of select="./@id"/>' src='<xsl:value-of select="./@src"/>' alt='<xsl:value-of select="./@alt"/>' &gt;
        <br/>
        Fig: <xsl:value-of select="./@title"/>
        </p>
      </xsl:when>
      <xsl:when test="name()='Chapter'">
        <xsl:call-template name="chapter"/> 
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$type='element'">
            <xsl:message>
Error: unknown element "<xsl:value-of select="name()"/>"
            </xsl:message>
            <xsl:if test='name()'>
              <xsl:element name='{name()}'>
                <xsl:copy-of select='./@*'/>
                <xsl:call-template name="verteiler"/> 
              </xsl:element>  
            </xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <xsl:copy-of select="."/>
          </xsl:otherwise>
        </xsl:choose>  
      </xsl:otherwise>  
    </xsl:choose>  
  </xsl:for-each>
</xsl:template>

<xsl:template name="atc_spec">
<xsl:call-template name="verteiler"/> 
</xsl:template>

<!-- handle chapter -->
<xsl:template name="chapter">
  <HTML>
  <HEAD>
    <TITLE>
      <xsl:value-of select="@title"/> - Confidential! 
    </TITLE>
  </HEAD>
  <BODY>
    This document is <font color="#FF0000">confidential!</font>
    <HR/>
    <H1>
      <xsl:value-of select="./@title"/> 
    </H1> 
    <xsl:if test="(./@isInternal='yes')"><p/><b>Chapter is for internal use only! Do not publish it.</b><br/><p/></xsl:if> 
    <!-- beschreibung ausgeben -->
    <xsl:apply-templates select="descr"/>
   </BODY>
  </HTML>
</xsl:template>

<!-- handle AT command -->
<xsl:template name="at_command">
  <HTML>
  <HEAD>
    <TITLE>
      <xsl:if test="(./@tag!='') or (./@tag2!='')">
        <xsl:if test="not(./@isATCommand='no')">AT</xsl:if>
        <xsl:value-of select="./@tag"/><xsl:value-of select="./@tag2"/>
      </xsl:if>  
      &#160;<xsl:value-of select="@title"/> - Confidential!
    </TITLE>
  </HEAD>
  <BODY>
    This document is <font color="#FF0000">confidential!</font>
    <HR/>
    <H1>
      <xsl:if test="(./@tag!='') or (./@tag2!='')">
        <xsl:if test="not(./@isATCommand='no')">AT</xsl:if>
        <xsl:value-of select="./@tag"/><xsl:value-of select="./@tag2"/>
      </xsl:if>  
      &#160;<xsl:value-of select="./@title"/> 
    </H1> 
    <xsl:if test="(./@isInternal='yes')"><p/><b>Command is for internal use only! Do not publish it.</b><br/><p/></xsl:if> 
    <!--
    \label{atc_<xsl:value-of select="./@id"/>}
    -->
    <!-- beschreibung ausgeben -->
    <xsl:apply-templates select="descr"/>
    <br/><br/>
    <!-- syntax table and command descriptions only if specified -->
    <!-- syntax table ausgeben -->
    <xsl:if test="(count(./exec)>0) or (count(./test)>0) or 
      (count(./read)>0) or (count(./write)>0)">
    <!--<table frame="box"> -->
    <table border="1" rules="all">
      <colgroup><col width="700" valign="top"/></colgroup>
     <!-- test command -->
      <xsl:if test="count(./test)>0"><xsl:apply-templates select="test" mode="syntax"/></xsl:if>
      <!-- exec command -->
      <xsl:if test="count(./exec)>0">
        <xsl:for-each select="exec">
          <xsl:apply-templates select="." mode="syntax"/>
        </xsl:for-each>
      </xsl:if>
      <!-- read command -->
      <xsl:if test="count(./read)>0"><xsl:apply-templates select="read" mode="syntax"/></xsl:if>
      <!-- write command -->
      <xsl:if test="count(./write)>0">
        <xsl:for-each select="write">
          <xsl:apply-templates select="." mode="syntax"/>
        </xsl:for-each>
      </xsl:if>
    </table>
    <p/>
    <!-- properties -->
    <xsl:call-template name="properties"/> 
    <p/>
    </xsl:if>
    <!-- URCs ausgeben --> 
    <xsl:call-template name="urc"/>
    <!-- IRCs ausgeben --> 
    <xsl:call-template name="irc"/>

    <!-- command descriptions ausgeben -->
    <xsl:if test="(count(./exec)>0) or (count(./test)>0) or 
      (count(./read)>0) or (count(./write[@isInternal!='yes'])>0)">
      <H2>Command Description:</H2>
      <!-- test command -->
      <xsl:apply-templates select="test" mode="descr"/>
      <!-- exec command -->
      <xsl:if test="count(./exec)>0">
        <xsl:for-each select="exec">
          <xsl:apply-templates select="." mode="descr"/>
        </xsl:for-each>
      </xsl:if>
      <!-- read command -->
      <xsl:apply-templates select="read" mode="descr"/>
      <!-- write command -->
      <xsl:if test="count(./write)>0">
        <xsl:for-each select="write[@isInternal!='yes']">
          <xsl:apply-templates select="." mode="descr"/>
        </xsl:for-each>
      </xsl:if>
    </xsl:if>
    
    <!-- internal command descriptions ausgeben -->
    <xsl:if test="count(./write[@isInternal='yes'])>0">
      <H2>Command Description (for internal use only, do not publish!):</H2>
      <xsl:for-each select="write">
        <xsl:if test="./@isInternal='yes'">
          <xsl:apply-templates select="." mode="descr"/>
        </xsl:if>
      </xsl:for-each>
    </xsl:if>  

    <!-- parameter description ausgeben -->
    <xsl:if test="count(./pdescriptions)>0">
    <H2>Parameters:</H2>
    <xsl:apply-templates select="pdescriptions"/>
    </xsl:if>
    <!-- notes ausgeben -->
    <!-- TBD: hier unterscheiden zwischen den verschiedenen Typen von Notes -->
    <!-- TBD: notes ueber itemize ausgeben -->
    <!--
    <xsl:if test="count(./note)>0 or count(./exec/note) > 0 or
    count(./test/note) > 0 or count(./read/note) > 0 or 
    count(./write/note) > 0">
    <H2>Notes:</H2>
    <xsl:apply-templates select="note"/>
    <xsl:apply-templates select="exec" mode="note"/>
    <xsl:apply-templates select="test" mode="note"/>
    <xsl:apply-templates select="read" mode="note"/>
    <xsl:apply-templates select="write" mode="note"/>
    -->
    <!-- <xsl:value-of select="at_command/note"/>  -->
    <xsl:if test="count(//note[@category!='developer' and @category!='internal'])>0">
      <H2>Notes:</H2>
      <ul>
      <xsl:for-each select="//note">
        <xsl:if test="./@category!='developer' and ./@category!='internal'">
        <li>
          <xsl:call-template name="verteiler"/> 
        </li>
        </xsl:if>
      </xsl:for-each>
      </ul>
    </xsl:if>  
    <xsl:if test="count(//note[@category='developer' or @category='internal'])>0">
      <H2>Notes (for internal use only, do not publish!):</H2>
      <ul>
      <xsl:for-each select="//note">
        <xsl:if test="./@category='developer' or ./@category='internal'">
        <li>
          <xsl:call-template name="verteiler"/> 
        </li>
        </xsl:if>
      </xsl:for-each>
      </ul>
    </xsl:if>  
     <!-- examples ausgeben -->
    <xsl:if test="count(./example)>0">
      <H2>Examples:</H2>
      <ul>
      <xsl:for-each select="./example">
        <li>
        <xsl:call-template name="verteiler"/>
        </li>
      </xsl:for-each>
      </ul>
    </xsl:if>
    <!-- products ausgeben -->
    <xsl:if test="count(./product)>0">
      <H2>Products:</H2>
      <xsl:for-each select="./product">
        <xsl:call-template name="verteiler"/>
        <xsl:if test="not(position()=last())"><xsl:text>, </xsl:text></xsl:if>
      </xsl:for-each>
    </xsl:if>
    <!-- subsections ausgeben -->
    <xsl:for-each select="//subsection">
      &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
      <H2>
        <xsl:value-of select="./@title"/>
        <xsl:if test="./@category='internal'">
          (for internal use only!)
        </xsl:if>  
        <xsl:if test="./@category='open'">
          (open issue!)
        </xsl:if>  
      </H2>
      <xsl:call-template name="verteiler"/> 
    </xsl:for-each>
    <!-- References ausgeben -->
    <xsl:if test="count(./lref)>0">
      <H2>References:</H2>
      <xsl:for-each select="./lref">
        <xsl:call-template name="verteiler"/>
        <xsl:if test="not(position()=last())"><xsl:text>, </xsl:text></xsl:if>
      </xsl:for-each>
    </xsl:if>
   </BODY>
  </HTML>
</xsl:template>

<!-- handle subsubsection -->
<xsl:template name="subsubsection">
  &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
  <H3>
    <xsl:value-of select="./@title"/>
    <xsl:if test="./@category='internal'">
      (for internal use only!)
    </xsl:if>  
    <xsl:if test="./@category='open'">
      (open issue!)
    </xsl:if>  
  </H3>
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<!--
<xsl:template match="note">
  <p/>
    <xsl:call-template name="verteiler"/> 
  <p/>
</xsl:template>
-->

<!-- command descriptions -->
<xsl:template name="execd" match="exec" mode="descr"> 
  <p/>
  <xsl:apply-templates select="./descr"/>
</xsl:template>

<xsl:template match="test" mode="descr"> 
  <p/>
  <xsl:apply-templates select="./descr"/>
</xsl:template>

<xsl:template match="read" mode="descr"> 
  <p/>
  <xsl:apply-templates select="./descr"/>
</xsl:template>

<xsl:template name="writed"  match="write" mode="descr"> 
  <p/>
  <xsl:apply-templates select="./descr"/>
</xsl:template>

<xsl:template match="descr" name="descr">
  <xsl:call-template name="verteiler"/>
</xsl:template>

<xsl:template match="header" name="header">
  <br/>
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<!-- 
<xsl:template match="note">
  <xsl:call-template name="verteiler"/> 
</xsl:template>
-->

<!-- syntax tables -->
<xsl:template name="execs" match="exec" mode="syntax"> 
  <tr>
      <td><small>Exec command</small><xsl:if test="./@isInternal='yes'"> (for <b>internal</b> use only!)</xsl:if><br/><br/>
          <xsl:if test="(@ATcommand!='')"><xsl:value-of select="@ATcommand"/><xsl:apply-templates select="./params"/></xsl:if>
          <xsl:if test="(@ATcommand='')">
          <xsl:if test="count(./header)>0">
              <xsl:apply-templates select="./header"/><br/>
          </xsl:if>
          <xsl:if test="not(../@isATCommand='no')">AT</xsl:if>
          <xsl:value-of select="../@tag"/><xsl:apply-templates select="./params"/>
          </xsl:if>
      </td>
  </tr>
  <tr>
      <td><small>Response</small><br/>
          <xsl:apply-templates select="./response"/>
      </td>
  </tr>
</xsl:template>

<xsl:template match="test" mode="syntax"> 
  <tr>
      <td><small>Test command</small><br/><br/>
          <xsl:if test="not(../@isATCommand='no')">AT</xsl:if>
          <xsl:value-of select="../@tag"/>=? 
      </td>
  </tr>    
  <tr>
      <td><small>Response</small><br/><br/>
          <xsl:apply-templates select="./response"/>
      </td>
  </tr>
</xsl:template>

<xsl:template match="read" mode="syntax"> 
  <tr>
      <td><small>Read command</small><br/><br/>
          <xsl:if test="@ATcommand!=''"><xsl:value-of select="@ATcommand"/></xsl:if>
          <xsl:if test="@ATcommand=''">
          <xsl:if test="not(../@isATCommand='no')">AT</xsl:if>
          <xsl:value-of select="../@tag"/>? 
          </xsl:if>
      </td>
  </tr>    
  <tr>
      <td><small>Response</small><br/><br/>
          <xsl:apply-templates select="./response"/>
      </td>
  </tr>
</xsl:template>

<xsl:template name="writes" match="write" mode="syntax"> 
  <tr>
      <td><small>Write command</small><xsl:if test="./@isInternal='yes'"> (for <b>internal</b> use only!)</xsl:if><br/><br/>
          <xsl:if test="count(./header)>0">
                <xsl:apply-templates select="./header"/><br/>
          </xsl:if>
          <xsl:if test="not(../@isATCommand='no')">AT</xsl:if>
          <xsl:value-of select="../@tag"/>=<xsl:apply-templates select="./params"/>
      </td>
  </tr>    
  <tr>
      <td><small>Response</small><br/><br/>
          <xsl:apply-templates select="./response"/>
      </td>
  </tr>
</xsl:template>

<!-- command responses -->
<xsl:template match="exec/response"> 
  <xsl:call-template name="verteiler"/>
</xsl:template>

<xsl:template match="test/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template match="read/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template match="write/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<!-- command params -->
<xsl:template match="exec/params"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template match="write/params"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template name="line">
  <br/>
  <xsl:if test="@isOptional='yes'">[</xsl:if> 
  <xsl:if test="@prefix!='no'"><tt><xsl:value-of select="../@prefix"/></tt></xsl:if><xsl:call-template name="verteiler"/> 
  <xsl:if test="@isOptional='yes'">]</xsl:if> 
</xsl:template>

<xsl:template name="rc_code">
  <br/>
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template match="paramlist" name="paramlist">
  <!-- handle prefix -->
  <xsl:if test="@prefix='comma'">,</xsl:if> 
  <!-- if it is an optional parameter list, start it with '[' -->
  <xsl:if test="@req='no'">[</xsl:if>
  <xsl:call-template name="verteiler"/>
  <!-- if it was an optional parameter list, terminate it with ']' -->
  <xsl:if test="@req='no'">]</xsl:if>
</xsl:template>

<xsl:template match="param" name="param">
  <!-- if it is an optional parameter, start it with '[' -->
  <xsl:if test="./@req='no'">[</xsl:if>
  <!-- handle prefix -->
  <xsl:if test="@prefix='comma' or @prefix=''">, </xsl:if> 
  <xsl:call-template name="verteiler"/>
  <!-- if it was an optional parameter, terminate it with ']' -->
  <xsl:if test="@req='no'">]</xsl:if>
</xsl:template>

<!-- reference to parameter -->
<xsl:template name="pref">&lt;pref ref='<xsl:value-of select="./@ref"/>'/&gt;</xsl:template>

<!-- reference to tag -->
<xsl:template name="tref">
  &lt;tref ref='<xsl:value-of select="./@ref"/>'/&gt;
</xsl:template>

<!-- reference to table -->
<xsl:template name="tabref">&lt;tabref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Table</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~TABREF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>
  /&gt;
</xsl:template>

<!-- reference to AT command -->
<xsl:template name="atcref">
  &lt;atcref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Section</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~ATCREF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>
  /&gt;
</xsl:template>

<!-- reference to chapter -->
<xsl:template name="cref">
  &lt;cref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Chapter</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~CREF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>
  /&gt;
</xsl:template>

<!-- reference to subsection -->
<xsl:template name="sref">
  &lt;sref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Section</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~SREF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>
  /&gt;
</xsl:template>

<!-- reference to subsubsection -->
<xsl:template name="ssref">
  &lt;ssref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Section</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~SSREF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>
  /&gt;
</xsl:template>

<!-- reference to image -->
<xsl:template name="img_ref">
  &lt;img_ref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Figure</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~IMG_REF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>
  /&gt;
</xsl:template>

<!-- TBD: literature reference -->
<xsl:template name="lref">
  <xsl:call-template name="verteiler"/>
</xsl:template>

<xsl:template name="pdescriptions" match="pdescriptions">
  <dl>
  <xsl:for-each select="./pdescr">
    <xsl:if test="(./@isNonVolatile='no') and (./@at_and_w='no')">
       <xsl:if test="(./@suppressPowerupValueError='no') and ((count(./value[@powerup = 'yes']) + count(./prange[@powerup != ''])) = 0)">
         <xsl:message terminate="no">
Error: Missing powerup value for parameter '<xsl:value-of select="./@id"/>' for document with id '<xsl:value-of select="/*/@id"/>'
         </xsl:message>
       </xsl:if>
    </xsl:if>
    <dt><tt>
    &lt;&lt;a name='<xsl:value-of select="./@id"/>'/&gt;<xsl:value-of select="./@tag"/>&gt;</tt>
      <xsl:if test="(./@isNonVolatile='yes')">
         <xsl:if test="(./@suppressDeliveryValueError='no') and ((count(./value[@delivery = 'yes']) + count(./prange[@delivery != ''])) = 0)">
           <xsl:message terminate="no">
Error: Missing delivery value for parameter '<xsl:value-of select="./@id"/>' for document with id '<xsl:value-of select="/*/@id"/>'
           </xsl:message>
         </xsl:if>
         <small><sup>(NV)</sup></small>
      </xsl:if>
      <xsl:if test="(./@at_and_w='yes')">
         <xsl:if test="(./@suppressDeliveryValueError='no') and ((count(./value[@delivery = 'yes']) + count(./prange[@delivery != ''])) = 0)">
           <xsl:message terminate="no">
Error: Missing delivery value for parameter '<xsl:value-of select="./@id"/>' for document with id '<xsl:value-of select="/*/@id"/>'
           </xsl:message>
         </xsl:if>
         ~~~START_USE_THIS_FOR_PRODUCTS_WITH_AT_AND_W~~~
         <small><sup>(&amp;W)</sup></small>
         ~~~END_USE_THIS_FOR_PRODUCTS_WITH_AT_AND_W~~~
      </xsl:if>
      <xsl:if test="(./@cscs='yes')">
         <small><sup>(+CSCS)</sup></small>
      </xsl:if>
      <xsl:if test="(./@snfw='yes')">
         ~~~START_USE_THIS_FOR_PRODUCTS_WITH_SNFW~~~
         <small><sup>(^SNFW)</sup></small>
         ~~~END_USE_THIS_FOR_PRODUCTS_WITH_SNFW~~~
      </xsl:if>
      <xsl:if test="(./@at_and_v='yes')">
         ~~~START_HIDE_THIS_FOR_PRODUCTS_WITH_HIDE_AND_V_TAGS~~~
         <small><sup>(&amp;V)</sup></small>
         ~~~END_HIDE_THIS_FOR_PRODUCTS_WITH_HIDE_AND_V_TAGS~~~
      </xsl:if>
      <xsl:if test="(./@geranUtranAvail='yes')">
         ~~~START_USE_THIS_FOR_PRODUCTS_WITH_GERAN_UTRAN~~~ 
         <small><sup>(&amp;paramTagAcTGeranUtran;)</sup></small>
         ~~~END_USE_THIS_FOR_PRODUCTS_WITH_GERAN_UTRAN~~~
      </xsl:if>
      <xsl:if test="(./@cdmaAvail='yes')">
         ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CDMA~~~ 
         <small><sup>(&amp;paramTagAcTCdma;)</sup></small>
         ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CDMA~~~
      </xsl:if>
      <xsl:if test="(./@eutranAvail='yes')">
         ~~~START_USE_THIS_FOR_PRODUCTS_WITH_EUTRAN~~~ 
         <small><sup>(&amp;paramTagAcTeUTRAN;)</sup></small>
         ~~~END_USE_THIS_FOR_PRODUCTS_WITH_EUTRAN~~~
      </xsl:if>
    </dt>         
    <dd>
      <xsl:if test="@name!='' or @type!=''">
        <xsl:value-of select="./@name"/> 
        <xsl:if test="@type!='unspecified'">
          <xsl:text> (</xsl:text><xsl:value-of select="./@type"/>)
          <xsl:if test="./@isInternal='yes'"> (parameter is for <b>internal</b> use only!)</xsl:if><br/>
        </xsl:if>  
      </xsl:if> 
      <xsl:for-each select="child::node()">
        <xsl:choose> 
          <xsl:when test="name()='header'">
            <xsl:call-template name="verteiler"/>
            <br/>
          </xsl:when>
          <xsl:when test="name()='descr'">
            <xsl:call-template name="verteiler"/>
            <br/>
          </xsl:when>
          <xsl:when test="name()='value'">
            <table>
             <tr>
               <td valign="top">
                 <xsl:if test="(./@default='yes')">[</xsl:if>
                 <xsl:if test="(../@type='string')">"</xsl:if>
                 <xsl:value-of select="./@v"/>
                 <xsl:if test="(../@type='string')">"</xsl:if>
                 <xsl:if test="(./@default='yes')">]</xsl:if>
                 <xsl:if test="(./@factory='yes')">
                   <small><sup>(&amp;F)</sup></small>
                 </xsl:if>
                 <xsl:if test="(./@delivery='yes')">
                   <small><sup>(D)</sup></small>
                 </xsl:if>
                 <xsl:if test="(./@powerup='yes')">
                   <small><sup>(P)</sup></small>
                 </xsl:if>
                </td>
               <td valign="top"><xsl:if test="count(./child)>0">-</xsl:if></td>
               <td valign="top">
                 <xsl:if test="(./@isInternal='yes')"><b>(for internal use only, do not publish!)</b><br/></xsl:if>
                 <xsl:call-template name="verteiler"/> 
               </td>  
              </tr>
            </table>          
          </xsl:when>
          <xsl:when test="name()='prange'">
            <table>
            <tr>
            <td valign="top">
              <xsl:if test="./@min=./@default">[</xsl:if>
              <xsl:if test="(../@type='string')">"</xsl:if>
              <xsl:value-of select="./@min"/>
              <xsl:if test="(../@type='string')">"</xsl:if>
              <xsl:if test="./@min=./@default">]</xsl:if>
              <xsl:if test="./@min=./@factory">
                <small><sup>(&amp;F)</sup></small>
              </xsl:if>
              <xsl:if test="./@min=./@powerup">
                <small><sup>(P)</sup></small>
              </xsl:if>
              <xsl:if test="./@min=./@delivery">
                <small><sup>(D)</sup></small>
              </xsl:if>
              ...
              <xsl:if
              test="(./@min!=./@default)and(./@max!=./@default)and(./@default!='')">
                 [<xsl:if test="(../@type='string')">"</xsl:if>
                 <xsl:value-of select="./@default"/>
                 <xsl:if test="(../@type='string')">"</xsl:if>] ...
              </xsl:if>
              <xsl:if
              test="(./@min!=./@factory)and(./@max!=./@factory)and(./@factory!='')">
                <xsl:if test="(../@type='string')">"</xsl:if>
                <xsl:value-of select="./@factory"/>
                <xsl:if test="(../@type='string')">"</xsl:if>
                <small><sup>(&amp;F)</sup></small>
                ...
              </xsl:if>
              <!-- the following may cause duplicate values with different tags;
                   this will handled within post_process_html.pl in function
                   handle_prange_values()
                   -->
              <xsl:if
              test="(./@min!=./@powerup)and(./@max!=./@powerup)and(./@powerup!='')">
                <xsl:if test="(../@type='string')">"</xsl:if>
                <xsl:value-of select="./@powerup"/>
                <xsl:if test="(../@type='string')">"</xsl:if>
                <small><sup>(P)</sup></small>
                ...
              </xsl:if>
              <xsl:if
              test="(./@min!=./@delivery)and(./@max!=./@delivery)and(./@delivery!='')">
                <xsl:if test="(../@type='string')">"</xsl:if>
                <xsl:value-of select="./@delivery"/>
                <xsl:if test="(../@type='string')">"</xsl:if>
                <small><sup>(D)</sup></small>
                ...
              </xsl:if>

              <xsl:if test="./@max=./@default">[</xsl:if>
              <xsl:if test="(../@type='string')">"</xsl:if>
              <xsl:value-of select="./@max"/>
              <xsl:if test="(../@type='string')">"</xsl:if>
              <xsl:if test="./@max=./@default">]</xsl:if>
              <xsl:if test="./@max=./@factory">
                <small><sup>(&amp;F)</sup></small>
              </xsl:if>
              <xsl:if test="./@max=./@powerup">
                <small><sup>(P)</sup></small>
              </xsl:if>
              <xsl:if test="./@max=./@delivery">
                <small><sup>(D)</sup></small>
              </xsl:if>
            </td> 
            <td valign="top"> <xsl:if test="count(./child)>0">-</xsl:if> </td>
            <td valign="top">
              <xsl:call-template name="verteiler"/> 
            </td>  
            </tr>
            </table>
          </xsl:when>
        </xsl:choose>
      </xsl:for-each>
    </dd>  
  </xsl:for-each>
  </dl>
</xsl:template>

<xsl:template name="urc">
  <xsl:if test="count(./urc)>0">
    <H2>Unsolicited Result Codes:</H2>
    <table><xsl:for-each select="./urc">
      <xsl:if test="(./@isInternal='yes')">
        <tr><td><br/></td></tr>
        <tr><td><b>The following URC is for internal use only! Do not publish it.</b></td></tr>
      </xsl:if> 
      &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
      <xsl:if test="count(./header)>0">
        <tr><td> 
          <xsl:apply-templates select="./header"/> 
        </td></tr>
      </xsl:if>
      <tr><td>
        <xsl:apply-templates select="./response"/> 
      </td></tr>
      <tr><td>
        <xsl:apply-templates select="./descr"/> 
      </td></tr>
      <tr><td> 
      </td></tr>
    </xsl:for-each></table>
    <p/>
  </xsl:if>
</xsl:template>

<xsl:template name="urc2">
  <table>
    <xsl:if test="(./@isInternal='yes')">
      <tr><td><b>The following URC is for internal use only! Do not publish it.</b></td></tr>
    </xsl:if> 
    &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
    <xsl:if test="count(./header)>0">
      <tr><td> 
        <xsl:apply-templates select="./header"/> 
      </td></tr>
    </xsl:if>
    <tr><td>
      <xsl:apply-templates select="./response"/> 
    </td></tr>
    <tr><td>
      <xsl:apply-templates select="./descr"/> 
    </td></tr>
    <tr><td> 
    </td></tr>
  </table>
</xsl:template>

<xsl:template match="urc/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<!-- reference to URC -->
<xsl:template name="uref">
  &lt;uref ref='<xsl:value-of select="./@ref"/>' <xsl:if test="./@v!=''"> v='<xsl:value-of select="./@v"/>'</xsl:if> <xsl:if test="./@withQuotes!=''"> withQuotes='<xsl:value-of select="./@withQuotes"/>'</xsl:if> <xsl:if test="./@fmt='long'"> fmt='long'</xsl:if> /&gt;
</xsl:template>


<xsl:template name="irc">
  <xsl:if test="count(./irc)>0">
    <H2>Intermediate Result Codes:</H2>
    <table><xsl:for-each select="./irc">
      &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
      <xsl:if test="count(./header)>0">
        <tr><td> 
          <xsl:apply-templates select="./header"/> 
        </td></tr>
      </xsl:if>
      <tr><td>
        <xsl:apply-templates select="./response"/> 
      </td></tr>
      <tr><td>
        <xsl:apply-templates select="./descr"/> 
      </td></tr>
      <tr><td> 
      </td></tr>
    </xsl:for-each></table>
    <p/>
  </xsl:if>
</xsl:template>

<xsl:template match="irc/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<!-- reference to IRC -->
<xsl:template name="iref">
  &lt;iref ref='<xsl:value-of select="./@ref"/>' <xsl:if test="./@v!=''">v='<xsl:value-of select="./@v"/>'</xsl:if> <xsl:if test="./@fmt='long'">fmt='long'</xsl:if> /&gt;
</xsl:template>

<!-- reference to table -->
<!--
<xsl:template name="tabref">
  &lt;tabref ref='<xsl:value-of select="./@ref"/>'
  <xsl:if test="./@type='yes'">Table</xsl:if><xsl:if test="./@extra!=''"><xsl:value-of select="./@extra"/></xsl:if>   
  <xsl:if test="./@number='yes'"> 0.0</xsl:if>
  <xsl:if test="./@title='yes'">, ~~~TABREF~TITLE~~~</xsl:if>
  <xsl:if test="./@page='yes'">, pg. 0</xsl:if>&gt;
</xsl:template>
-->

<!-- reference to LI -->
<xsl:template name="liref">
  &lt;liref ref='<xsl:value-of select="./@ref"/>' <xsl:if test="./@fmt='long'">fmt='long'</xsl:if> /&gt;
</xsl:template>

<xsl:template name="properties"> 
  <table border="1">
  <tr>
  ~~~START_SKIP_THIS_FOR_PRODUCTS_WITH_CDMA_ONLY~~~ 
  <td>PIN</td><td>DevSIM</td>
  ~~~END_SKIP_THIS_FOR_PRODUCTS_WITH_CDMA_ONLY~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_ASC0~~~ 
  <td>ASC0</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_ASC0~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_ASC1~~~ 
  <td>ASC1</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_ASC1~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MUX1~~~ 
  <td>MUX1</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MUX1~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MUX2~~~ 
  <td>MUX2</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MUX2~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MUX3~~~ 
  <td>MUX3</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MUX3~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_USB~~~ 
  <td>USB0</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_USB~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MDM~~~ 
  <td>MDM</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MDM~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_APP~~~ 
  <td>APP</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_APP~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_GERAN_UTRAN~~~ 
  <td>&amp;engineAcT;</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_GERAN_UTRAN~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CDMA~~~ 
  <td>&amp;actCdma;</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CDMA~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_EUTRAN~~~ 
  <td>&amp;actEUTRAN;</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_EUTRAN~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_AIRPLANEMODE~~~
  <td>Airplane</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_AIRPLANEMODE~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CHARGEONLY~~~
  <td>Charge</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CHARGEONLY~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_ALARMMODEONLY~~~
  <td>Alarm</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_ALARMMODEONLY~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CWTESTMODE~~~
  <td>CwTest</td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CWTESTMODE~~~
  <td>Last</td>
  </tr>
  <tr>
  ~~~START_SKIP_THIS_FOR_PRODUCTS_WITH_CDMA_ONLY~~~ 
  <td align="center">
      <xsl:if test="./@isPinProtected='yes'">&#8226;</xsl:if>
      <xsl:if test="./@isPinProtected=''">&#8226;</xsl:if>
      <xsl:if test="./@isPinProtected='partial'">o</xsl:if>
      <xsl:if test="./@isPinProtected='no'">&#160;</xsl:if></td>
  <td align="center">&#160;
      <xsl:if test="./@isDevSimProtected='yes'">&#8226;</xsl:if>
      <xsl:if test="./@isDevSimProtected='partial'">o</xsl:if></td>
  ~~~END_SKIP_THIS_FOR_PRODUCTS_WITH_CDMA_ONLY~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_ASC0~~~ 
  <td align="center">&#160;
      <xsl:if test="./@asc0Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@asc0Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@asc0Avail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_ASC0~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_ASC1~~~ 
  <td align="center">&#160;
      <xsl:if test="./@asc1Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@asc1Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@asc1Avail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_ASC1~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MUX1~~~ 
  <td align="center">&#160;
      <xsl:if test="./@muxChannel1Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel1Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel1Avail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MUX1~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MUX2~~~ 
  <td align="center">&#160;
      <xsl:if test="./@muxChannel2Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel2Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel2Avail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MUX2~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MUX3~~~ 
  <td align="center">&#160;
      <xsl:if test="./@muxChannel3Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel3Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel3Avail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MUX3~~~ 
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_USB~~~ 
  <td align="center">&#160;
      <xsl:if test="./@usb0Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@usb0Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@usb0Avail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_USB~~~    
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_MDM~~~ 
  <td align="center">&#160;
      <xsl:if test="./@mdmPortAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@mdmPortAvail=''">&#8226;</xsl:if>
      <xsl:if test="./@mdmPortAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_MDM~~~    
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_APP~~~ 
  <td align="center">&#160;
      <xsl:if test="./@appPortAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@appPortAvail=''">&#8226;</xsl:if>
      <xsl:if test="./@appPortAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_APP~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_GERAN_UTRAN~~~ 
  <td align="center">&#160;
      <xsl:if test="./@geranUtranAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@geranUtranAvail=''">&#8226;</xsl:if>
      <xsl:if test="./@geranUtranAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_GERAN_UTRAN~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CDMA~~~ 
  <td align="center">&#160;
      <xsl:if test="./@cdmaAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@cdmaAvail=''">&#8226;</xsl:if>
      <xsl:if test="./@cdmaAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CDMA~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_EUTRAN~~~ 
  <td align="center">&#160;
      <xsl:if test="./@eutranAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@eutranAvail=''">&#8226;</xsl:if>
      <xsl:if test="./@eutranAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_EUTRAN~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_AIRPLANEMODE~~~
  <td align="center">&#160;
      <xsl:if test="./@airplaneModeAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@airplaneModeAvail=''">&#8226;</xsl:if>
      <xsl:if test="./@airplaneModeAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_AIRPLANEMODE~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CHARGEONLY~~~
  <td align="center">&#160;
      <xsl:if test="./@chargeOnlyModeAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@chargeOnlyModeAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CHARGEONLY~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_ALARMMODEONLY~~~
  <td align="center">&#160;
      <xsl:if test="./@alarmModeAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@alarmModeAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_ALARMMODEONLY~~~
  ~~~START_USE_THIS_FOR_PRODUCTS_WITH_CWTESTMODE~~~
  <td align="center">&#160;
      <xsl:if test="./@cwTestModeAvail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@cwTestModeAvail='partial'">o</xsl:if></td>
  ~~~END_USE_THIS_FOR_PRODUCTS_WITH_CWTESTMODE~~~
  <td align="center">&#160;
      <xsl:if test="./@isLastCommand='yes'">&#8226;</xsl:if>
      <xsl:if test="./@isLastCommand='partial'">o</xsl:if></td>
  </tr>
  </table>
</xsl:template>
 
<!-- handling of examples and related -->
<xsl:template name="code">
<p/>
<small>
<table>
  <colgroup><col width="100" valign="top"/> 
            <col width="100" valign="top"/>
            <col width="400" valign="top"/>
  </colgroup>
  <xsl:for-each select="cline">
  <tr>
  <xsl:if test="./ctext/@fmt!='long'">
    <td valign="top"><tt><xsl:apply-templates select="./ctext"/></tt></td>
    <td>          </td>
    <td valign="top"><xsl:apply-templates select="./ccomment"/></td>
  </xsl:if>
  <xsl:if test="./ctext/@fmt='long'">
    <td valign="top" width="800"><tt><xsl:apply-templates select="./ctext"/></tt></td>
  </xsl:if>
  </tr>
  </xsl:for-each>
</table>
</small>
<p/>
</xsl:template>

<xsl:template match="cline/ctext"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template match="cline/ccomment"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template name="list"> 
  <UL>
  <xsl:for-each select="li">
    <LI>
    <xsl:call-template name="verteiler"/> 
    </LI>
  </xsl:for-each>
  </UL>
</xsl:template>

<xsl:template name="num_list"> 
  <p>
  <xsl:for-each select="li">
    <xsl:if test="@id != ''">
      &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
    </xsl:if>
    <xsl:choose> 
      <xsl:when test="@bt = 'square'">[</xsl:when>
      <xsl:when test="@bt = 'angle'">&lt;</xsl:when>
      <xsl:when test="@bt = 'brace'">{</xsl:when>
      <xsl:when test="@bt = 'parenthesis'">(</xsl:when>
    </xsl:choose>
    <xsl:number count="li"/>
    <xsl:choose> 
      <xsl:when test="@bt = 'square'">]</xsl:when>
      <xsl:when test="@bt = 'angle'">&gt;</xsl:when>
      <xsl:when test="@bt = 'brace'">}</xsl:when>
      <xsl:when test="@bt = 'parenthesis'">)</xsl:when>
      <xsl:otherwise>.</xsl:otherwise>
    </xsl:choose>
    <font color="#FFFFFF">_</font>
    <xsl:call-template name="verteiler"/><br/>
  </xsl:for-each>
  </p>
</xsl:template>

<xsl:template name="sup"> 
  <SUP>
  <xsl:call-template name="verteiler"/> 
  </SUP>
</xsl:template>
<xsl:template name="sub"> 
  <SUB>
  <xsl:call-template name="verteiler"/> 
  </SUB>
</xsl:template>

<xsl:template name="table"> 
  <br/>
  <xsl:if test="./@id!=''">
    &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
  </xsl:if>
  &lt;TABLE 
  <xsl:if test="@rules != ''"> rules='<xsl:value-of select="@rules"/>'</xsl:if>
  <xsl:if test="@border != ''"> border='<xsl:value-of select="@border"/>'</xsl:if>
  &gt;
  <xsl:if test="count(./caption)>0">
    <xsl:for-each select="caption">
      <caption>Table 0.0: <xsl:call-template name="verteiler"/></caption>
    </xsl:for-each>
  </xsl:if>
  <xsl:if test="./thead/@isHidden!='yes'"> 
    <THEAD>
    <xsl:for-each select="thead/tline">
      <TR>
        <xsl:for-each select="tcol">
          &lt;TCOL<xsl:if test="@width != ''"> width='<xsl:value-of select="@width"/>'</xsl:if><xsl:if test="@colspan != ''"> colspan='<xsl:value-of select="@colspan"/>'</xsl:if>&gt;<B><xsl:call-template name="verteiler"/></B>&lt;/TCOL&gt;
        </xsl:for-each>
      </TR>
    </xsl:for-each>
    </THEAD>
  </xsl:if> 
  <xsl:if test="count(./tbody)>0">
    <TBODY>
    <xsl:for-each select="tbody/tline">
      <TR>
        <xsl:for-each select="tcol">
          &lt;TCOL<xsl:if test="@width != ''"> width='<xsl:value-of select="@width"/>'</xsl:if><xsl:if test="@colspan != ''"> colspan='<xsl:value-of select="@colspan"/>'</xsl:if>&gt;<xsl:call-template name="verteiler"/>&lt;/TCOL&gt;
        </xsl:for-each>
      </TR>
    </xsl:for-each>
    </TBODY>
  </xsl:if>
  <xsl:if test="count(./tfoot)>0">
    <SMALL><TFOOT>
    <xsl:for-each select="tfoot/tline">
      <TR>
        <xsl:for-each select="tcol">
          &lt;TCOL<xsl:if test="@width != ''"> width='<xsl:value-of select="@width"/>'</xsl:if><xsl:if test="@colspan != ''"> colspan='<xsl:value-of select="@colspan"/>'</xsl:if>&gt;<xsl:call-template name="verteiler"/>&lt;/TCOL&gt;
        </xsl:for-each>
      </TR>
    </xsl:for-each>
    </TFOOT></SMALL>
  </xsl:if>
  &lt;/TABLE&gt;
</xsl:template>

<!-- some help constructs -->
<xsl:template match="*" mode="detect-type">element</xsl:template>
<xsl:template match="text()" mode="detect-type">text</xsl:template>
<xsl:template match="comment()" mode="detect-type">comment</xsl:template>
<xsl:template match="processing-instruction()" mode="detect-type">pi</xsl:template>

</xsl:stylesheet>
<!-- vim: expandtab ts=2 ai wm=5 
  -->
