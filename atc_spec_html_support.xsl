<?xml version="1.0" encoding="ISO-8859-1"?>

<!-- 
$Author: SP49027 $
$Revision: \main\bln\9 $
$Source: Z:\z_org_sw\application\specs\atc_spec\etc\atc_spec_html.xsl $
$Date: 2002/5/29 14:35:20 $
-->

<xsl:stylesheet version="1.0" 
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html"/>

<xsl:template match="/">
  <xsl:for-each select="//urc">
    <xsl:call-template name="urc"/> 
  </xsl:for-each>
  <xsl:for-each select="//irc">
    <xsl:call-template name="irc"/> 
  </xsl:for-each>
  <xsl:for-each select="//ol">
    <xsl:call-template name="num_list"/> 
  </xsl:for-each>
  <xsl:for-each select="//table">
    <xsl:call-template name="table"/> 
  </xsl:for-each>
</xsl:template>

<xsl:template name="urc">
___urc_start___
   ___id_start___
      <xsl:value-of select="./@id"/>
   ___id_end___
   ___header_start___
      <xsl:apply-templates select="./header"/> 
   ___header_end___
   ___response_start___
      <xsl:apply-templates select="./response"/> 
   ___response_end___
   ___description_start___
      <xsl:apply-templates select="./descr"/> 
   ___description_end___
___urc_end___
</xsl:template>

<xsl:template name="irc">
___irc_start___
   ___id_start___
      <xsl:value-of select="./@id"/>
   ___id_end___
   ___header_start___
      <xsl:apply-templates select="./header"/> 
   ___header_end___
   ___response_start___
      <xsl:apply-templates select="./response"/> 
   ___response_end___
   ___description_start___
      <xsl:apply-templates select="./descr"/> 
   ___description_end___
___irc_end___
</xsl:template>

<xsl:template name="num_list"> 
  <xsl:for-each select="li">
    ___num_list_entry_start___
    <xsl:value-of select="./@id"/>,
    <xsl:value-of select="./@bt"/>,
    <xsl:number count="li"/>,
    <xsl:call-template name="verteiler"/>
    ___num_list_entry_end___
  </xsl:for-each>
</xsl:template>

<xsl:template name="table">
___table_start___
   ___id_start___
      <xsl:value-of select="./@id"/>
   ___id_end___
   ___caption_start___
   <xsl:if test="count(./caption)>0">
     <xsl:for-each select="caption">
       <xsl:call-template name="verteiler"/>
     </xsl:for-each>
   </xsl:if>
   ___caption_end___
___table_end___
</xsl:template>

<xsl:template match="urc/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template match="irc/response"> 
  <xsl:call-template name="verteiler"/> 
</xsl:template>

<xsl:template name="verteiler">
  <xsl:for-each select="child::node()">
    <xsl:variable name="type">
      <xsl:apply-templates mode="detect-type" select="."/>
    </xsl:variable>
    <xsl:choose> 
      <!--
      <xsl:when test="name()='at_command'">
        <xsl:call-template name="at_command"/> 
      </xsl:when>
      <xsl:when test="name()='atc_spec'">
        <xsl:call-template name="atc_spec"/> 
      </xsl:when>
      -->
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
      <!--
      <xsl:when test="name()='opt_more_lines'">
        <xsl:call-template name="opt_more_lines"/> 
      </xsl:when>
      -->
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
      <!-- reference to subsubsection -->
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
      <xsl:when test="name()='code'">
        <xsl:call-template name="code"/> 
      </xsl:when>
      <xsl:when test="name()='ul'">
        <xsl:call-template name="list"/> 
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
        <p align="center">
        &lt;a name='<xsl:value-of select="./@id"/>'/&gt;
        &lt;img id='<xsl:value-of select="./@id"/>' src='<xsl:value-of select="./@src"/>' alt='<xsl:value-of select="./@alt"/>' &gt;
        <br/>
        Fig: <xsl:value-of select="./@title"/>
        </p>
      </xsl:when>
      <!--
      <xsl:when test="name()='Chapter'">
        <xsl:call-template name="chapter"/> 
      </xsl:when>
      -->
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

<!--
<xsl:template name="atc_spec">
<xsl:call-template name="verteiler"/> 
</xsl:template>
-->

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

<!--
<xsl:template name="opt_more_lines">
  <br/>[...]]<xsl:if test="@isOptional='yes'">]</xsl:if> 
</xsl:template>
-->

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
<xsl:template name="pref">
  &lt;pref ref='<xsl:value-of select="./@ref"/>'/&gt;
</xsl:template>

<!-- reference to tag -->
<xsl:template name="tref">
  &lt;tref ref='<xsl:value-of select="./@ref"/>'/&gt;
</xsl:template>

<!-- reference to table -->
<xsl:template name="tabref">
  &lt;tabref ref='<xsl:value-of select="./@ref"/>'
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

<xsl:template match="pdescriptions">
  <dl>
  <xsl:for-each select="./pdescr">
    <dt><tt>
    &lt;&lt;a name='<xsl:value-of select="./@id"/>'/&gt;<xsl:value-of select="./@tag"/>&gt;</tt>
      <xsl:if test="(./@at_and_w='yes')">
         <small><sup>(&amp;W)</sup></small>
      </xsl:if>
      <xsl:if test="(./@snfw='yes')">
         <small><sup>(^SNFW)</sup></small>
      </xsl:if>
      <xsl:if test="(./@at_and_v='yes')">
         <small><sup>(&amp;V)</sup></small>
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
      <xsl:if test="descr!=''">
        <xsl:apply-templates select="./descr"/> <br/>
      </xsl:if>
      <xsl:if test="count(./value)>0">
        <table>
         <xsl:for-each select="./value"><tr>
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
          </tr></xsl:for-each>
        </table>
      </xsl:if>
      <xsl:if test="count(./prange)>0">
        <table>
        <xsl:for-each select="./prange"><tr>
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
        </tr></xsl:for-each>
        </table>
      </xsl:if>
    </dd>  
  </xsl:for-each>
  </dl>
</xsl:template>

<!-- reference to URC -->
<xsl:template name="uref">
  &lt;uref ref='<xsl:value-of select="./@ref"/>' <xsl:if test="./@v!=''"> v='<xsl:value-of select="./@v"/>'</xsl:if> <xsl:if test="./@withQuotes!=''"> withQuotes='<xsl:value-of select="./@withQuotes"/>'</xsl:if> <xsl:if test="./@fmt='long'"> fmt='long'</xsl:if> /&gt;
</xsl:template>

<!-- reference to IRC -->
<xsl:template name="iref">
  &lt;iref ref='<xsl:value-of select="./@ref"/>' <xsl:if test="./@v!=''">v='<xsl:value-of select="./@v"/>'</xsl:if> <xsl:if test="./@fmt='long'">fmt='long'</xsl:if> /&gt;
</xsl:template>

<xsl:template name="properties"> 
  <table border="1">
  <tr>
  <td>PIN</td><td>DevSIM</td><td>ASC0</td>
  <!-- enable this for projects only which support ASC1     
  <td>ASC1</td>
  -->
  <td>MUX1</td>
  <td>MUX2</td><td>MUX3</td>
  </tr>
  <tr>
  <td align="center">
      <xsl:if test="./@isPinProtected='yes'">&#8226;</xsl:if>
      <xsl:if test="./@isPinProtected=''">&#8226;</xsl:if>
      <xsl:if test="./@isPinProtected='partial'">o</xsl:if>
      <xsl:if test="./@isPinProtected='no'">&#160;</xsl:if></td>
  <td align="center">&#160;
      <xsl:if test="./@isDevSimProtected='yes'">&#8226;</xsl:if>
      <xsl:if test="./@isDevSimProtected='partial'">o</xsl:if></td>
  <td align="center">&#160;
      <xsl:if test="./@asc0Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@asc0Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@asc0Avail='partial'">o</xsl:if></td>
  <!-- enable this for projects only which support ASC1     
  <td align="center">&#160;
      <xsl:if test="./@asc1Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@asc1Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@asc1Avail='partial'">o</xsl:if></td>
  -->    
  <td align="center">&#160;
      <xsl:if test="./@muxChannel1Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel1Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel1Avail='partial'">o</xsl:if></td>
  <td align="center">&#160;
      <xsl:if test="./@muxChannel2Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel2Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel2Avail='partial'">o</xsl:if></td>
  <td align="center">&#160;
      <xsl:if test="./@muxChannel3Avail='yes'">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel3Avail=''">&#8226;</xsl:if>
      <xsl:if test="./@muxChannel3Avail='partial'">o</xsl:if></td>
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

<!-- not used here
<xsl:template name="table"> 
  <TABLE border="1" align="center">
  <xsl:if test="./thead/@isHidden!='yes'"> 
    <B><THEAD>
    <xsl:for-each select="thead/tline">
      <TR>
        <xsl:for-each select="tcol">
          <TD>
            <xsl:call-template name="verteiler"/> 
          </TD>
        </xsl:for-each>
      </TR>
    </xsl:for-each>
    </THEAD></B>
  </xsl:if> 
  <xsl:if test="count(./tbody)>0">
    <TBODY>
    <xsl:for-each select="tbody/tline">
      <TR>
        <xsl:for-each select="tcol">
          <TD>
            <xsl:call-template name="verteiler"/> 
          </TD>
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
          <TD>
            <xsl:call-template name="verteiler"/> 
          </TD>
        </xsl:for-each>
      </TR>
    </xsl:for-each>
    </TFOOT></SMALL>
  </xsl:if>
  </TABLE>
</xsl:template>
-->

<!-- some help constructs -->
<xsl:template match="*" mode="detect-type">element</xsl:template>
<xsl:template match="text()" mode="detect-type">text</xsl:template>
<xsl:template match="comment()" mode="detect-type">comment</xsl:template>
<xsl:template match="processing-instruction()" mode="detect-type">pi</xsl:template>

</xsl:stylesheet>
<!-- vim: expandtab ts=2 ai wm=5 
  -->
