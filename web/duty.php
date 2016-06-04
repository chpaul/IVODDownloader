<?php
/**
 * Created by PhpStorm.
 * User: chuyu
 * Date: 5/28/14
 * Time: 5:44 AM
 */
if (!array_key_exists('Lglts', $_POST)) {
    header("Location: http://1985.paulyu.org/");
    exit;
}
if (!array_key_exists('Duty_ST_Date', $_POST)) {
    $Start_Date = "2010-08-22" . " 00:00:00";
} else {
    $Start_Date = $_POST["Duty_ST_Date"] . " 00:00:00";
}
$Sdate = DateTime::createFromFormat('Y-m-d h:i:s', $Start_Date);
if (!array_key_exists('Duty_ET_Date', $_POST)) {
    $End_Date = "2020-02-22" . " 00:00:00";
} else {
    $End_Date = $_POST["Duty_ET_Date"] . " 00:00:00";
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

function DisplayLgltRecord()
{
    $db = new PDO('sqlite:./bin/iVOD_LY.sqlite');
    $VOLName =  explode("@", $_POST["Lglts"])[0]; #VOL@Lglt,Lglt
    $Lglt ="";
    foreach( explode(",", explode("@", $_POST["Lglts"])[1]) as $lg)
        $Lglt = $Lglt . $lg . ",";
    $Lglt =        substr($Lglt,0, strlen($Lglt)-1);
    global $Start_Date, $End_Date, $_POST;

    if ($Lglt == "未定" or strpos($Lglt, "委員會") !== false) {//領養整個委員會 或是 院會
        echo "<div id=\"FullTable\" style=\"width: 100%;\"><table>";
        if($Lglt == "未定")
        {
            echo "<caption>" . $Start_Date. "~" . $End_Date . "  " . $VOLName . " 的任務 [調查". "院會"."]</caption>\n\t";
        }
        else
        {
            echo "<caption>" . $Start_Date . "~" . $End_Date . "  " . $VOLName . " 的任務 [調查". $Lglt ."]</caption>\n\t";
        }
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
        echo "\t\t<th  scope=\"col\"  id=\"METDEC\">會議內容</th>\n\t</tr>\n\t</thead>\n";
        if($Lglt == "未定")
        {
            $LgltDate = $db->query("SELECT *  FROM iVOD_FullMeeting where (ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date . "\") AND  CM_NAM=\"" ."院會" . "\"  ORDER BY ST_TIM DESC ,CM_NAM ASC;");
        }
        else
        {
            $LgltDate = $db->query("SELECT *  FROM iVOD_FullMeeting where (ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date . "\") AND  CM_NAM=\"" .$Lglt  . "\"  ORDER BY ST_TIM DESC ,CM_NAM ASC;");
        }
        $rowOdd = true;
        foreach ($LgltDate as $row) {
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
            echo "\t</tr>\n";
        }
    } else {
        //領養個人委員
        echo "<div id=\"LgltTable\" style=\"width: 100%;\"><table>";
        echo "<caption>" . $Start_Date . "~" .$End_Date . "  " . $VOLName . " 的任務 [調查". $Lglt ."]</caption>\n\t";
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
        echo "\t\t<th  scope=\"col\"  id=\"METDEC\">會議內容</th>\n\t</tr>\n\t</thead>\n";
        $rowOdd = true;


        $lstLglt = explode(",", $Lglt);
        foreach ($lstLglt as $lg) {
            $LgltDate = $db->query("SELECT *  FROM iVOD_Lglt where (ST_TIM Between \"" . $Start_Date . "\"  AND \"" . $End_Date . "\") AND  CH_NAM=\"" . $lg . "\"  ORDER BY ST_TIM DESC ,CM_NAM ASC, LGLTIM ASC;");

            foreach ($LgltDate as $row) {
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
                echo "\t</tr>\n";
            }
        }
    }


    echo "</tbody></table></div>\n";

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
    <center><a href="https://www.facebook.com/groups/724111940953135/" target="_blank"><img  src="logo.jpg" alt="公民覺醒聯盟國會調查兵團"/></a> <br>
    <?php
    DisplayLgltRecord();
    ?>
</div>
</body>
</html>
