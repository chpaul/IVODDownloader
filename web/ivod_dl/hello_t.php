<?php
//
// GPL 
//
// ver. 0.1 
// http://jangmt.com/
// by mtchang.tw@gmail.com 2014.9.26

$webapp['name'] = '立法院IVOD下載器';
$webapp['req_doc']  = 'http://jangmt.com/?p=108';
$webapp['useragent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36';
// 存在那個目錄底下
$webapp['webroot_path'] = dirname(__FILE__);
$webapp['download'] 	= 'download';
// php 在哪裡
$webapp['phppwd']		= dirname(dirname(__FILE__));
$downloadURL = "";
if ( isset($_GET['url']))
    $downloadURL = $_GET['url']
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="favicon.ico">

    <title><?php echo $webapp['name']; ?></title>

    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="dist/css/starter-template.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>
    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="hello_t.php"><?php echo $webapp['name']; ?></a>
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="hello_t.php">START</a></li>
            <li><a href="http://jangmt.com/?p=108">ABOUT</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>

    <div class="container">

        
        <div class="row">
        <div class="col-xs-12 col-sm-8 col-md-8">
                
        <h1><?php echo $webapp['name']; ?></h1>
        <p>程式說明：<a href="<?php echo $webapp['req_doc']; ?>"><?php echo $webapp['req_doc']; ?></a></p>  
        <p>立法院隨選視訊網址:<a href="http://ivod.ly.gov.tw/Legislator/Index">http://ivod.ly.gov.tw/Legislator/Index</a></p>
		<p>範例網址：http://ivod.ly.gov.tw/Play/VOD/76472/300K (因為這個委員講的比較短，所以用這段)</p>
        <p>預設儲存目錄：<?php echo $webapp['download']; ?></p> 
            
        <form name="input" action="hello_t.php?action=showinfo" method="POST">
        <div class="input-group">
          <span class="input-group-addon"> 選個 IVOD 網址：</span>
          <input name="ivodurl" type="text" class="form-control" placeholder="請貼上來自立法院網站的 IVOD 網址" value=<?php echo $downloadURL;?>>
        </div>
		 <div class="checkbox">
		<label>
		  <input name="ivod_only_hd" type="checkbox" checked> 只抓高畫質 1M 的影片
		</label>
		</div>
		<button type="submit" class="btn btn-default">提交</button>
        <br>
        </form>
            
        </div>
        </div>
                
            
        <div class="row">
            <div class="col-xs-12 col-sm-6 col-md-8">
            <?php
            // 取得網頁原始碼，處理成為可以用的
            //echo 'debug:<br>';
            //var_dump($_POST);
			//var_dump($webapp);
			//echo '<hr>';

            // example:
            // 這個委員發言比較短,測試速度比較快
            // $ivodurl = 'http://ivod.ly.gov.tw/Play/VOD/76472/300K';
            // $ivodurl = 'http://ivod.ly.gov.tw/Play/Full/7959/1M';

			// 網址判斷是否要抓高畫質的 1M
			$ivodurl = '';
			$ivodurl = $_POST['ivodurl'];
			$ivod_only_hd = $_POST['ivod_only_hd'];
			if($ivod_only_hd != NULL) {
				$ivodurl_tmp = $ivodurl;
				$ivodurl = preg_replace('/300K/', "1M", $ivodurl_tmp);
			}			
			
            // 建立CURL連線
            $ch = curl_init();
			
            // 檢查 url 的資料,正確才抓內容
            if($ivodurl != NULL) {
                // 設定擷取的URL網址
                curl_setopt($ch, CURLOPT_URL, "$ivodurl");
                curl_setopt($ch, CURLOPT_HEADER, false);
				curl_setopt($ch, CURLOPT_USERAGENT, $webapp['useragent']);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);
                $url_html_cache = curl_exec($ch);
            }
                
            ?>
            </div>
        </div>  
            
        <div class="row">
            <div class="col-xs-12 col-sm-8 col-md-8">
            <?php
            if($_GET['action'] == 'showinfo') {
				
				// 分析網頁內的內容資訊，以決定檔案名稱
				# Create a DOM parser object
				$dom = new DOMDocument();

				# Parse the HTML from Google.
				# The @ before the method call suppresses any warnings that
				# loadHTML might throw because of invalid HTML in the page.
				@$dom->loadHTML($url_html_cache);
				
				$i=0;
				foreach($dom->getElementsByTagName('p') as $link) {
					// print_r($link);
					$html_content_preg = preg_replace('/ /', "", $link->nodeValue);
					if($html_content_preg != '') {
						$html_content['nodeValue'][$i] = $html_content_preg;
						if(preg_match_all('/第[0-9]{1,2}屆第[0-9]{1,2}會期/', $html_content_preg)) {
							$html_content['com_name'] = $html_content_preg;
						}
						if(preg_match_all('/會議時間：/', $html_content_preg)) {
							$html_content['com_time'] = preg_replace('/會議時間：/', '', $html_content_preg);
						}
						if(preg_match_all('/委員名稱：/', $html_content_preg)) {
							$html_content['com_person'] = preg_replace('/委員名稱：/', '', $html_content_preg);
						}
						if(preg_match_all('/委員發言時間：/', $html_content_preg)) {
							$html_content['com_say_time'] = preg_replace('/委員發言時間：/', '', $html_content_preg);
						}						
						if(preg_match_all('/會議簡介：/', $html_content_preg)) {
							$html_content['com_note'] = preg_replace('/會議簡介：/', '', $html_content_preg);
						}
						$i++;
					}
				}
				//echo '<pre>';
				//print_r($html_content);
				//echo '</pre>';
				

				
                // 找出 readyplayer 的網址，轉成 url 
				// 這段用 RE 來抓比較快, $ivod_manifest_url 為播放內容
                // 如果立院不亂改的話 , 這個 RE parten 應該可以用。 2014.9.27
                // 1 PASS RE
                preg_match('/readyPlayer\\(.*\)/', $url_html_cache, $match_readyplayer);
                // 2 pass RE
                preg_match('/,\'.*\\)/', $match_readyplayer[0], $match_url);
                // 3 pass RE
                preg_match('/,\'.*\\)/', $match_url[0], $match_manifest_url_re3);
                // pass 4 RE
                $ivod_manifest_url_re4 = preg_replace('/,\'/', "", $match_manifest_url_re3[0]);
                // pass 5 RE
                $ivod_manifest_url = preg_replace('/\'\\)/', "", $ivod_manifest_url_re4);
                // var_dump($ivod_manifest_url);
                //echo "<br>正規表示式結束</pre>";
				

				
				// 取得 manifest 內容,讀出影片長度
                curl_setopt($ch, CURLOPT_URL, "$ivod_manifest_url");
                curl_setopt($ch, CURLOPT_HEADER, false);
				curl_setopt($ch, CURLOPT_USERAGENT, $webapp['useragent']);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);
                $url_manifest_cache = curl_exec($ch);	
				// echo "<pre>$url_manifest_cache</pre>";
                // 關閉CURL連線
                curl_close($ch);
				// 分析 manifest xml 讀出秒數
				$xml=simplexml_load_string($url_manifest_cache);
				$duration_sec = $xml->duration;
				$duration_min = $xml->duration/60;
				
				// ---- 此影片內容資訊 -----
				echo '<pre>';
				echo '影片網址：<a href="'.$ivodurl.'">'.$ivodurl.'</a><br>';
				echo '影片長度秒數：'.$duration_sec.'，約為 '.$duration_min.' 分鐘。<br>';
				echo '會期：'.$html_content['com_name'].'<br>';
				echo '委員名稱：'.$html_content['com_person'].'<br>';
				echo '委員發言時間'.$html_content['com_say_time'].'<br>';
				echo '會議時間：'.$html_content['com_time'].'<br>';
				echo '會議簡介：'.$html_content['com_note'].'<br>';
				//echo '下載後的檔案將存放於目錄：'.$webapp['webroot_path'].'/'.$webapp['download'].'<br>';
				$download_filename = $html_content['com_person'].'_'.$html_content['com_time'].'.flv';
				$download_filename = preg_replace('/[\\:-]/', "_", $download_filename);
				echo '檔名將會是：'.$download_filename .'<br>';
				echo $match_readyplayer[0] .'   1<br>';
				echo $match_url[0] .'      2<br>';
				echo $match_manifest_url_re3[0] .'    3<br>';
				echo $ivod_manifest_url_re4[0] .'      4<br>';
				echo $$ivod_manifest_url .'                 5<br>';
				echo '</pre>';				
				
				if($duration_sec > 0 ){
					echo '
					<form name="input" action="hello_t.php?action=download" method="POST">
					<div class="input-group">
					  <span class="label label-default"> 是否立即抓取這個影片？(抓取時間會因網路速度及影片長度有影響，需要耐心等待)</span>
					  <input type="hidden" name="ivod_manifest_url" value="'.$ivod_manifest_url.'">
					  <input type="hidden" name="download_filename" value="'.$download_filename.'">
					</div>
					<br>
					<button type="submit" class="btn btn-default">立即抓取影片</button>
					<button id="cancel_get" type="button" class="btn btn-danger">放棄，重來一次</button>
					<br>
					</form>
					';
				}
		
            }
            ?>
            </div>
        </div>
        
        
        <div class="row">
            <div class="col-xs-12 col-sm-8 col-md-8">
            <?php
            if($_GET['action'] == 'download') {
                $download_filename = $_POST['download_filename'];
                // 先使用時間當檔名, 後須需要改變為會議內容
                $filename = $webapp['webroot_path'].'/'.$webapp['download'].'/' .$download_filename;

                echo '<pre>';
				echo '影片抓取中，請耐心等待...(會因為網路速度及影片長度關係有所影響)<br>';
				//echo "檔案預計存放：".$filename.'<br>';
				echo '</pre>';
				
                // 執行抓取的動作
				$ivod_manifest_url = $_POST['ivod_manifest_url'];
                $cmd_ivodurl_get ='php AdobeHDS_new.php --quality high --delete --useragent "'.$webapp['useragent'].'" --outfile "'.$filename.'" --manifest "'.$ivod_manifest_url.'"';
				$cmd_output = 'NULL';
				$cmd_return_var = 1;
				// 命令列中文環境為 big5 編碼,所以需要轉碼否則無法中文檔名
				$cmd_ivodurl_get_big5 = mb_convert_encoding($cmd_ivodurl_get, "utf-8", "auto");
                echo "<pre>cmd命令:".$cmd_ivodurl_get.'</pre>';
                #echo '<pre>下載過程：<br>';
                $cmd_output = system("$cmd_ivodurl_get_big5",$cmd_return_var);
				#echo $cmd_output;
                #echo '</pre>';


				// var_dump($cmd_return_var);
				if($cmd_return_var == 0) {
                    $URLFile = 'Download File: <a href=./download/' . $download_filename. '>'.$download_filename.'</a>';
                    echo '<br>' . $URLFile;
                    //header('Content-type:application/force-download'); //告訴瀏覽器 為下載
                    //header('Content-Transfer-Encoding: Binary'); //編碼方式
                    //header('Content-Disposition:attachment;filename=./download/'.$download_filename); //檔名
                    //@readfile($filename);

				}else{
					echo '<button id="cancel_get" type="button" class="btn btn-warning">下載失敗</button>';
				}
			}
            ?>
            </div>
        </div>

		
    </div><!-- /.container -->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="dist/js/jquery.min.js"></script>
    <script src="dist/js/bootstrap.min.js"></script>
	
	<script type="text/javascript">
	$(document).ready(function(){
	  $("#cancel_get").click(function(){
		document.location.href="hello_t.php";
	  });
	});
	</script>
	
  </body>
</html>
