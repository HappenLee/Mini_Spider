### Mini_Spider

**Mini_Spider** uses Python to develop a mini-crawler program, mini_spider.py, to achieve breadth-first fetching of seed links and save URLs that match a particular pattern to disk.


* **Program Operation:**

```

python mini_spider.py -c spider.conf

```


* **Configuration File Conf:**

```
[spider]
Url_list_file:./urls;  seed file path
Output_directory:./output;  grab results store directory
Max_depth: 1;  maximum grasp depth (seed 0)
Crawl_interval: 1;  grab interval. Unit: sec. 
Crawl_timeout: 1;  grab timeout. Unit: sec.
Target_url:. *. (gif|png|jpg|bmp) $; target storage page URL pattern (regular expression) needed to be stored.
Thread_count: 8; thread number of fetching
```

* **Seed Socument Link:**

Http://www.sina.com.cn/

* **Other Supplements**

Support command line parameter handling:
      **Specifically include: -h (help), -v (version), -c (configuration file).**
