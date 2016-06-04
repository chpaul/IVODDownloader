<?php
/**
 * Created by PhpStorm.
 * User: chuyu
 * Date: 5/27/14
 * Time: 5:14 AM
 */
    ini_set('include_path',ini_get('include_path'). PATH_SEPARATOR. './library');
    //ini_set('include_path',ini_get('include_path'). './Zend');
    $CommitteeQuery = array();

    if(!array_key_exists('Meeting_ST_Date',$_POST) )
    {
        $Start_Date = "2010-08-22" ." 00:00:00";
    }
    else
    {
        $Start_Date = $_POST["Meeting_ST_Date"] ." 00:00:00";
    }


    $Sdate  = DateTime::createFromFormat('Y-m-d h:i:s', $Start_Date);

    if(!array_key_exists('Meeting_ET_Date',$_POST) )
    {
        $End_Date = "2020-02-22" ." 00:00:00";
    }
    else
    {
        $End_Date = $_POST["Meeting_ET_Date"] ." 00:00:00";
    }



    $Edate = DateTime::createFromFormat('Y-m-d h:i:s', $End_Date);


    if($Edate<$Sdate)
    {
        $tmp =$Sdate;
        $Sdate = $Edate;
        $Edate = $tmp;
    }

    $Edate->add(new DateInterval('P1D'));

    $Start_Date =  $Sdate->format('Y-m-d') ;
    $End_Date =  $Edate->format('Y-m-d');

    $db = new PDO('sqlite:./bin/iVOD_LY.sqlite');
    if( array_key_exists('Committee',$_POST))
    {
        $CommitteeString = "";
        foreach ($_POST['Committee'] as $selectedOption)
            $CommitteeString = $CommitteeString . "CM_NAM = \"". $selectedOption ."\"OR ";
        $CommitteeString = substr($CommitteeString,0, strlen($CommitteeString)-3);
        $CommitteeString = " AND (" . $CommitteeString . ")";

        $FullMeetingDate = $db->query("SELECT * FROM iVOD_FullMeeting where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\"" .$CommitteeString ." ORDER BY ST_TIM DESC ,CM_NAM ASC");
        $LgltMeetingDate = $db->query("SELECT *  FROM iVOD_Lglt where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\"" . $CommitteeString ." ORDER BY ST_TIM DESC ,CM_NAM ASC, LGLTIM ASC");
    }
    else
    {
        $FullMeetingDate = $db->query("SELECT * FROM iVOD_FullMeeting where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\" ORDER BY ST_TIM DESC, CM_NAM ASC");
        $LgltMeetingDate = $db->query("SELECT *  FROM iVOD_Lglt where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\" ORDER BY ST_TIM DESC ,CM_NAM ASC,  LGLTIM ASC");
    }
    function DisplayLgltRecord($LgltRecords)
    {
        global $Start_Date, $End_Date;
        $CommitteeString = "";
        if( array_key_exists('Committee',$_POST))
        {
            foreach ($_POST['Committee'] as $selectedOption)
                $CommitteeString = $CommitteeString . $selectedOption .",";
            $CommitteeString =str_replace("委員會","",$CommitteeString);
            $CommitteeString =substr($CommitteeString,0,strlen($CommitteeString)-1) . " [委員發言片段]";
        }
        else
        {
            $CommitteeString = "院會,內政,外交及國防,經濟,財政,教育及文化,交通,司法及法制,社會福利及衛生環境,程序 [委員發言片段]";
        }


        echo "<div id=\"LgltTable\" style=\"width: 100%;\"><table>";
        echo "<caption>" . $Start_Date . "~" . $End_Date . " " . $CommitteeString . "</caption>\n\t";
        echo "<tbody>\n";
        echo "\t<col width=\"130px\"/>\n";
        echo "\t<col width=\"40px\"/>\n";
        echo "\t<col width=\"200px\"/>\n";
        echo "\t<col width=\"120px\"/>\n";
        echo "\t<col width=\"130px\"/>\n";
        //echo "\t<col width=\"30px\"/>\n";
        echo "\t<col width=\"99%\"/>\n";
        echo "\t<thead>\n\t<tr>\n\t\t<th scope=\"col\"  id=\"ST_TIM\">開會日期</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"LGLTIM\">發言時間</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"CM_NAM\">委員會</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"STAGE_\">會期</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"CH_NAM\">發言人</th>\n";
        //echo "\t\t<th  scope=\"col\"  id=\"FILNAM\">iVOD</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"METDEC\">會議內容</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"DOWNLOAD\">下載</th>\n\t</tr>\n\t</thead>\n";
        $rowOdd = true;
        foreach ($LgltRecords as $row) {
            if ($rowOdd == true) {
                echo "\t<tr class=\"odd\">\n";
            } else {
                echo "\t<tr>\n";
            }
            $rowOdd = !$rowOdd;
            echo "\t\t<td white-space=\"nowrap\" headers=\"ST_TIM\">" . explode(" ", $row['ST_TIM'])[0] . "</td>\n";
            echo "\t\t<td headers=\"LGLTIM\"><a href=\"http://ivod.ly.gov.tw/Play/VOD/" . $row["WZS_ID"] . "/300K\" target=\"_blank\">" . $row["LGLTIM"] . "</a></td>\n";
            echo "\t\t<td headers=\"CM_NAM\">" . $row["CM_NAM"] . "</td>\n";
            echo "\t\t<td headers=\"STAGE_\">第" . $row["STAGE_"] . "屆 第" . $row["DUTION"] . "會期</td>\n";
            echo "\t\t<td headers=\"CH_NAM\">" . $row["CH_NAM"] . "</td>\n";
            //echo "\t\t<td headers=\"FILNAM\"><a href=\"http://ivod.ly.gov.tw/Play/VOD/" . $row["WZS_ID"] . "/300K\" target=\"_blank\">Link</a></td>\n"; //http://ivod.ly.gov.tw/Play/VOD/75557/300K
            echo "\t\t<td headers=\"METDEC\"><div class=\"AlignLeft\" align=\"left\"  white-space=\"normal\" >" . $row["METDEC"] . "</div></td>\n";
            echo "\t\t<td headers=\"DOWNLOAD\"><a href=\"./ivod_dl/hello.php?url=http://ivod.ly.gov.tw/Play/VOD/" . $row["WZS_ID"] . "/300K\" target=\"_blank\">" . 'ivod_DL' . "</a></td>\n";
            echo "\t</tr>\n";
        }

        echo "</tbody></table></div>\n";
    }
    function DisplayFullRecord($FullRecord)
    {
        global $Start_Date, $End_Date;
        $CommitteeString = "";
        if( array_key_exists('Committee',$_POST))
        {
            foreach ($_POST['Committee'] as $selectedOption)
                $CommitteeString = $CommitteeString . $selectedOption .",";
            $CommitteeString =str_replace("委員會","",$CommitteeString);
            $CommitteeString =substr($CommitteeString,0,strlen($CommitteeString)-1)." [會議完整錄影]";
        }
        else
        {
            $CommitteeString = "院會,內政,外交及國防,經濟,財政,教育及文化,交通,司法及法制,社會福利及衛生環境,程序 [會議完整錄影]";
        }
        echo "<div id=\"FullTable\" style=\"width: 100%;\"><table>";
        echo "<caption>". $Start_Date . "~"  . $End_Date . " ".$CommitteeString. "</caption>\n\t";
        echo "<tbody>\n";
        echo "\t<col width=\"90px\"/>\n";
        echo "\t<col width=\"80px\"/>\n";
        echo "\t<col width=\"100px\"/>\n";
       // echo "\t<col width=\"30px\"/>\n";
        echo "\t<col width=\"99%\"/>\n";
        echo "\t<thead>\n\t<tr>\n\t\t<th scope=\"col\"  id=\"ST_TIM\">開會日期</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"CM_NAM\">委員會</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"STAGE_\">會期</th>\n";
        //echo "\t\t<th  scope=\"col\"  id=\"FILNAM\">iVOD</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"METDEC\">會議內容</th>\n";
        echo "\t\t<th  scope=\"col\"  id=\"DOWNLOAD\">下載</th>\n\t</tr>\n\t</thead>\n";
        $rowOdd = true;
        foreach ($FullRecord as $row) {
            if ($rowOdd == true) {
                echo "\t<tr class=\"odd\">\n";
            } else {
                echo "\t<tr>\n";
            }
            $rowOdd = !$rowOdd;
            echo "\t\t<td headers=\"ST_TIM\"><a href=\"http://ivod.ly.gov.tw/Play/Full/" . $row["MEREID"] . "/300K\" target=\"_blank\">" . $row['ST_TIM'] . "</a></td>\n";
            echo "\t\t<td headers=\"CM_NAM\">" . $row["CM_NAM"] . "</td>\n";
            echo "\t\t<td headers=\"STAGE_\">第" . $row["STAGE_"] . "屆 第" . $row["DUTION"] . "會期</td>\n";
            //echo "\t\t<td headers=\"FILNAM\"><a href=\"http://ivod.ly.gov.tw/Play/Full/" . $row["MEREID"] . "/300K\" target=\"_blank\">Link</a></td>\n"; //http://ivod.ly.gov.tw/Play/Full/75557/300K
            echo "\t\t<td headers=\"METDEC\"><div class=\"AlignLeft\" align=\"left\" white-space=\"pre\" word-wrap=\"break-word\">" . $row["METDEC"] . "</div></td>\n";
            echo "\t\t<td headers=\"DOWNLOAD\"><a href=\"./ivod_dl/hello.php?url=http://ivod.ly.gov.tw/Play/Full/" . $row["MEREID"] . "/300K\" target=\"_blank\">" . 'ivod_DL' . "</a></td>\n";
            echo "\t</tr>\n";
        }

        echo "</tbody></table></div>\n";
    }

    function DisplayVolunteerRecord()
    {
        require_once 'Zend/Gdata/Spreadsheets.php';
        require_once 'Zend/Gdata/ClientLogin.php';
        $setting = parse_ini_file("./bin/config.ini");
        $service = Zend_Gdata_Spreadsheets::AUTH_SERVICE_NAME;
        $client = Zend_Gdata_ClientLogin::getHttpClient($setting['email'],$setting['password'], $service);
        $spreadsheetService = new Zend_Gdata_Spreadsheets($client);

        #讀立委資料
        $query = new Zend_Gdata_Spreadsheets_ListQuery();
        $query->setSpreadsheetKey($setting['spreadsheetID']);
        $query->setWorksheetId($setting['WrkSheet_LgltInfo']);
        $listFeed = $spreadsheetService->getListFeed($query);
        $Lglt_info=[];
        for($i = 0;$i< sizeof($listFeed);$i++)
        {
            $Lglt=[];
            $rowData = $listFeed->entries[$i]->getCustom();
            foreach($rowData as $customEntry) {
                $Lglt[$customEntry->getColumnName()] = $customEntry->getText();
            }
            $Lglt_info[$Lglt["姓名"]]=$Lglt;
        }
        #讀志工
        $dictLegislator2Volunteer =[];
        $query = new Zend_Gdata_Spreadsheets_ListQuery();
        $query->setSpreadsheetKey($setting['spreadsheetID']);
        $query->setWorksheetId($setting['WrkSheet_VolunteerInfo']);
        $listFeed = $spreadsheetService->getListFeed($query);
        for($i = 0;$i< sizeof($listFeed);$i++)
        {
            $Vol=[];
            $rowData = $listFeed->entries[$i]->getCustom();
            foreach($rowData as $customEntry) {
                if ($customEntry->getText()=="")
                {
                    continue;
                }
                if(strpos( $customEntry->getColumnName(), "領養立委")!==false)
                {
                    if( !array_key_exists ("領養立委",$Vol))
                    {
                        $Vol["領養立委"] = array();
                    }
                    array_push( $Vol["領養立委"],$customEntry->getText());
                }
                else
                {
                    $Vol[$customEntry->getColumnName()] = $customEntry->getText();
                }
            }
            foreach($Vol["領養立委"] as $LgltName)
            {
                if( !array_key_exists ($LgltName,$dictLegislator2Volunteer))
                {
                    $dictLegislator2Volunteer[$LgltName] = array();
                }
                array_push( $dictLegislator2Volunteer[$LgltName] ,$Vol);
            }
        }
        global $CommitteeString, $Start_Date,$End_Date,$db;
        if( array_key_exists('Committee',$_POST))
        {
            $CommitteeString = "";
            foreach ($_POST['Committee'] as $selectedOption)
                $CommitteeString = $CommitteeString . "CM_NAM = \"". $selectedOption ."\"OR ";
            $CommitteeString = substr($CommitteeString,0, strlen($CommitteeString)-3);
            $CommitteeString = " AND (" . $CommitteeString . ")";

            $FullMeetingDate = $db->query("SELECT * FROM iVOD_FullMeeting where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\"" .$CommitteeString ." ORDER BY ST_TIM DESC ,CM_NAM ASC");
            $LgltMeetingDate = $db->query("SELECT *  FROM iVOD_Lglt where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\"" . $CommitteeString ." ORDER BY ST_TIM DESC ,CM_NAM ASC, LGLTIM ASC");
        }
        else
        {
            $FullMeetingDate = $db->query("SELECT * FROM iVOD_FullMeeting where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\" ORDER BY ST_TIM DESC, CM_NAM ASC");
            $LgltMeetingDate = $db->query("SELECT *  FROM iVOD_Lglt where ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date ."\" ORDER BY ST_TIM DESC ,CM_NAM ASC,  LGLTIM ASC");
        }
        $date = "";
        $CMNAME = "";
        foreach ($LgltMeetingDate as $row) {
            if( explode(" ", $row['ST_TIM'])[0] !=$date) #Print date
            {
                $date =  explode(" ", $row['ST_TIM'])[0];
                echo ("------------------------------------------------<br>\n". $date ."<br>\n");
                $CMNAME = "";
            }
            if( $row['CM_NAM'] != $CMNAME) # Print Committee Name
            {
                $CMNAME =  $row['CM_NAM'];
                echo ("<br>\n". $row['CM_NAM']);

                if( array_key_exists($row["CM_NAM"],$dictLegislator2Volunteer)) # 整個委員會的志工
                {
                    echo("\t\t\t");
                    $OutStr= "";
                    foreach($dictLegislator2Volunteer[$row["CM_NAM"]] as $vol)
                    {
                        $OutStr = $OutStr . $vol["fb名稱"].",";
                    }
                    $OutStr=  substr( $OutStr,0,strlen( $OutStr)-1) . "<br>\n";
                    echo($OutStr);
                }
                elseif($row['CM_NAM'] =="院會") #Output  未定
                {
                    echo("\t\t\t");
                    $OutStr= "";
                    foreach($dictLegislator2Volunteer["未定"] as $vol)
                    {
                        $OutStr = $OutStr . $vol["fb名稱"].",";
                    }
                    $OutStr=  substr( $OutStr,0,strlen( $OutStr)-1) . "<br>\n";
                    echo($OutStr);
                }
                else
                {
                    echo("<br>\n");
                }
            }

            if( array_key_exists($row["CH_NAM"],$dictLegislator2Volunteer)) # 單一認養志工
            {

                $OutStr= "";
                foreach($dictLegislator2Volunteer[ $row["CH_NAM"]] as $vol)
                {
                    $OutStr = $OutStr . $row["CH_NAM"] . "\t\t"."http://ivod.ly.gov.tw/Play/VOD/" . $row["WZS_ID"] . "/300K"."\t\t" . $vol["fb名稱"]."<br>\n" ;
                }
                echo($OutStr);
            }
        }

    }
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
		<title>公民覺醒聯盟國會調查兵團</title>
    <script type="text/javascript" src="./library/jquery-1.11.1.min.js"></script>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <style>
        @import url("./library/Table.css");
    </style>
<?php include_once("analyticstracking.php") ?>
</head>
<body>
<div id="content" style="width: 80%;margin:0 auto;">
    <center><a href="https://www.facebook.com/groups/724111940953135/" target="_blank"><img  src="logo.jpg" alt="公民覺醒聯盟國會調查兵團"/></a> <P>

    <a name="Top"/>
    <a href="#Clip">[委員發言片段]</a>
    <a href="#Full">[會議完整錄影]</a>
    <a href="#FB">[FB Post]</a>
    </center>
    <?php
    echo("<a name=\"Clip\"/>");
    DisplayLgltRecord($LgltMeetingDate);
    echo "<P><a name=\"Full\"/><a href=\"#Top\">[回頂端]</a><br>";
    DisplayFullRecord($FullMeetingDate);
    echo "<P><a name=\"FB\"/><a href=\"#Top\">[回頂端]</a><br>";
    DisplayVolunteerRecord($LgltMeetingDate);
    ?>
    <a href="#Top">[回頂端]</a>
</div>
</body>
</html>
