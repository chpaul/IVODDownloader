<?php
/**
 * Created by PhpStorm.
 * User: chuyu
 * Date: 5/27/14
 * Time: 12:32 AM
 */
$db = new PDO('sqlite:./bin/iVOD_LY.sqlite');
ini_set('include_path',ini_get('include_path'). PATH_SEPARATOR. './library');

/*

    $results = $db->query('SELECT DISTINCT CM_NAM FROM iVOD_Lglt');
    if(sqlite_num_rows($results)!=0)
    {
        foreach($results as $row) {
            echo  $row['CM_NAM'];
        }
    }

    if (mysql_num_rows($results)!=0)
    {
        echo '<select name="dropComtID" id="dropComtID">
          <option value=" " selected="selected">Choose one</option>';
        while($drop_2 = mysql_fetch_array( $result ))
        {
            echo '<option value="'.$drop_2['column_name'].'">'.$drop_2['column_name'].'</option>';
        }
        echo '</select>';
    }*/
function GetMembers()
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


        echo "<option value=\"" ;
        $LgltList = "";
        foreach($Vol["領養立委"] as $lg)
        {
            $LgltList = $LgltList . $lg . ",";
        }
        $LgltList = $Vol["fb名稱"] ."@".substr($LgltList,0,strlen($LgltList)-1) ;

        echo $LgltList;
        echo "\">";
        echo $Vol["fb名稱"];
        echo "</option>";

    }



}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
		<title>公民覺醒聯盟國會調查兵團</title>
    <script type="text/javascript" src="./library/jquery-1.11.1.min.js"></script>
    <script type="text/javascript">
       $(document).ready(function() {
            $('#selecctall').click(function(event) {  //on click
                if(this.checked) { // check select status
                    $('.checkbox1').each(function() { //loop through each checkbox
                        this.checked = true;  //select all checkboxes with class "checkbox1"
                    });
                }else{
                    $('.checkbox1').each(function() { //loop through each checkbox
                        this.checked = false; //deselect all checkboxes with class "checkbox1"
                    });
                }
            });
          });
    </script>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <?php include_once("analyticstracking.php") ?>

 </head>

<body>
<center><a href="https://www.facebook.com/groups/724111940953135/" target="_blank"><img  src="logo.jpg" alt="公民覺醒聯盟國會調查兵團"/></a></center>
<hr>
<div id="SpeechSearch" align="center" ><br>
<form action="display.php" method="post" name="Query" target="_self" onsubmit="return checkCheckBoxes(this);">

<p>會議查詢日期 : </p>
<?php
	$MeetingDate = array();
	$FullMeetingDate = $db->query("SELECT DISTINCT ST_TIM FROM iVOD_FullMeeting");
    foreach($FullMeetingDate as $row)
    {
        $date = explode(" ",$row['ST_TIM'])[0];
        if (! array_key_exists($date,$MeetingDate))
        {
            $MeetingDate [$date] = $date;
        }
    }

    $LgltMeetingDate = $db->query('SELECT DISTINCT ST_TIM FROM iVOD_Lglt');
    foreach($LgltMeetingDate as $row)
    {
        $date = explode(" ",$row['ST_TIM'])[0];
        if (! array_key_exists($date,$MeetingDate))
        {
            $MeetingDate [$date] = $date;
        }
    }

    arsort($MeetingDate);
    
?>
<p>開始時間

<select name="Meeting_ST_Date">
	<?php
		foreach( $MeetingDate as $date)
		{
			echo "<option value=\"" ;
			echo $date;
			echo "\">";
			echo $date;
			echo "</option>";
		
		}
	?>
</select>

~結束時間<select name="Meeting_ET_Date">
	<?php
		foreach( $MeetingDate as $date)
		{
			echo "<option value=\"" ;
			echo $date;
			echo "\">";
			echo $date;
			echo "</option>";
		
		}
	?>
</select></p>

    <p>委員會選擇 : <input id="selecctall" type="checkbox" >全委員會</p>
    <table width="600" border="1" >
      <tr>
        <td rowspan="3" valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="院會" minlength="2">院會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="內政委員會">內政委員會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="外交及國防委員會">外交及國防委員會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="經濟委員會">經濟委員會<P></td>
      </tr>
      <tr>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="財政委員會">財政委員會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="教育及文化委員會">教育及文化委員會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="交通委員會">交通委員會<P></td>
      </tr>
      <tr>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="司法及法制委員會">司法及法制委員會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="社會福利及衛生環境委員會">社會福利及衛生環境委員會<P></td>
        <td valign="middle"><input class="checkbox1" name="Committee[]" type="checkbox" value="程序委員會">程序委員會<P></td>
      </tr>
    </table>
    <label class="error" for="Committee[]" generated="true"></label>
<input value="會議查詢" type="submit">

</form>
</div>
<br><hr><br>
<br><br>

<!--
<div id="DutySearch" style="display: none;">
    <form action="duty.php" method="post" name="Query" target="_self" align="center">
        兵團成員任務查詢<br>
        <select name="Lglts">
        <?php
            //GetMembers();
        ?>
        </select>
        <br>開始時間

            <select name="Duty_ST_Date">
                <?php
                /*foreach( $MeetingDate as $date)
                {
                    echo "<option value=\"" ;
                    echo $date;
                    echo "\">";
                    echo $date;
                    echo "</option>";

                }*/
                ?>
            </select>

            ~結束時間<select name="Duty_ET_Date">
                <?php
                /*foreach( $MeetingDate as $date)
                {
                    echo "<option value=\"" ;
                    echo $date;
                    echo "\">";
                    echo $date;
                    echo "</option>";

                }*/
                ?>
            </select>
        <br>
    <input value="任務查詢" type="submit">

    </form>
</div>
<br><br><br><br>
<hr>
-->
<center> Developer: Chuan-Yih Yu paulyu[小老鼠]paulyu.org</center>
<center> 最後更新時間:
        <?php
        $UpdateTime =$db->query("SELECT * FROM UpdateTime");
        $UTimes= [];
        foreach($UpdateTime as $row)
        {
            $UTimes[$row['TableName']] =  $row['LastUpdateDateTime'];

        }
        echo ("<br>[委員發言片段]". $UTimes["iVOD_Lglt"] . "<br>[會議完整錄影]" .$UTimes["iVOD_FullMeeting"] );

        $handle = @fopen("./bin/log.txt", "r");
        $line ="";
        if ($handle) {
            while (($buffer = fgets($handle, 4096)) !== false) {
                $line = $buffer;
            }
            if (!feof($handle)) {
                echo "Error: unexpected fgets() fail\n";
            }
            fclose($handle);
            $lastRunTime = substr($line,37,19);
            echo  "<br>[程式執行檢查]" . $lastRunTime;
        }

        ?>
</center>
</body>
</html>
