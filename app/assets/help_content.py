# Help Content for Cari Kitab
import os

HELP_HTML = """
<div style="font-family: sans-serif; line-height: 1.6; color: #333;">
    <h1 style="color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 10px;">📖 Panduan Penggunaan Cari Kitab</h1>
    
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #198754;">1. Cara Mencari Kitab</h2>
        <ol>
            <li>Buka tab <b>Pencarian</b>.</li>
            <li>Ketik judul kitab atau nama penulis di kolom input (Gunakan bahasa Latin atau Arab).</li>
            <li>Tekan tombol <b>Cari</b> atau tekan <b>Enter</b>.</li>
            <li>Aplikasi akan mencari di berbagai sumber (Google, Shamela, Archive, dll).</li>
        </ol>
    </div>

    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #198754;">2. Mendownload PDF</h2>
        <ol>
            <li>Setelah hasil muncul, klik tombol <b>Download PDF</b> pada kartu kitab yang diinginkan.</li>
            <li>Jika Anda belum mengatur folder download di tab <b>Setting</b>, Anda akan diminta memilih lokasi simpan.</li>
            <li>Proses download akan berjalan di latar belakang (cek progress bar di bawah).</li>
        </ol>
    </div>

    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #198754;">3. Menggunakan AI Konsultan</h2>
        <ol>
            <li>Buka tab <b>AI Konsultan</b>.</li>
            <li>Tanyakan apa saja seputar kitab, misalnya: <i>"Rekomendasikan kitab fikih untuk pemula"</i>.</li>
            <li><b>Fitur Spesial:</b> Jika AI menyebutkan judul kitab (misal: Al-Umm), Anda bisa langsung <b>mengklik teks tersebut</b> untuk mengirimnya ke kotak pencarian secara otomatis.</li>
        </ol>
    </div>

    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 30px;">
        <h2 style="color: #198754;">4. Pengaturan (Setting)</h2>
        <ul>
            <li><b>API Keys:</b> Masukkan kunci Gemini Anda di sini (mendukung rotasi otomatis).</li>
            <li><b>Download Directory:</b> Tentukan folder permanen untuk menyimpan semua file PDF agar tidak ditanya setiap kali download.</li>
        </ul>
    </div>

    <h1 style="color: #d63384; border-bottom: 2px solid #d63384; padding-bottom: 10px;">📚 Daftar Referensi Kitab Klasik</h1>
    <p style="font-style: italic; color: #666;">Klik pada Judul (Latin) atau Judul (Arab) untuk mencari kitab tersebut.</p>

    <h2 style="color: #0d6efd;">1. Bidang Aqidah (Tauhid/Teologi)</h2>
    <ul>
        <li><a href="search:Al-Fiqh Al-Akbar">Al-Fiqh Al-Akbar</a> (<a href="search:الفقه الأكبر">الفقه الأكبر</a>) - <a href="search:Abu Hanifah">Imam Abu Hanifah</a></li>
        <li><a href="search:Al-Ibanah 'an Ushul Ad-Diyanah">Al-Ibanah 'an Ushul Ad-Diyanah</a> (<a href="search:الإبانة عن أصول الديانة">الإبانة عن أصول الديانة</a>) - <a href="search:Abu Al-Hasan Al-Asy'ari">Imam Abu Al-Hasan Al-Asy'ari</a></li>
        <li><a href="search:Al-Aqidah Ath-Thahawiyyah">Al-Aqidah Ath-Thahawiyyah</a> (<a href="search:العقيدة الطحاوية">العقيدة الطحاوية</a>) - <a href="search:Abu Ja'far Ath-Thahawi">Imam Abu Ja'far Ath-Thahawi</a></li>
        <li><a href="search:Kitab At-Tauhid">Kitab At-Tauhid</a> (<a href="search:كتاب التوحيد">كتاب التوحيد</a>) - <a href="search:Abu Mansur Al-Maturidi">Imam Abu Mansur Al-Maturidi</a></li>
        <li><a href="search:Al-Iqtishad fi Al-I'tiqad">Al-Iqtishad fi Al-I'tiqad</a> (<a href="search:الاقتصاد في الاعتقاد">الاقتصاد في الاعتقاد</a>) - <a href="search:Abu Hamid Al-Ghazali">Imam Abu Hamid Al-Ghazali</a></li>
        <li><a href="search:Al-Aqa'id An-Nasafiyyah">Al-Aqa'id An-Nasafiyyah</a> (<a href="search:العقائد النسفية">العقائد النسفية</a>) - <a href="search:Najmuddin An-Nasafi">Najmuddin An-Nasafi</a></li>
        <li><a href="search:Ummul Barahin">Ummul Barahin / As-Sanusiyyah</a> (<a href="search:أم البراهين">أم البراهين</a>) - <a href="search:Muhammad bin Yusuf As-Sanusi">Imam Muhammad bin Yusuf As-Sanusi</a></li>
        <li><a href="search:Jauharatut Tauhid">Jauharatut Tauhid</a> (<a href="search:جوهرة التوحيد">جوهرة التوحيد</a>) - <a href="search:Ibrahim Al-Laqqani">Ibrahim Al-Laqqani</a></li>
        <li><a href="search:Aqidatul Awam">Aqidatul Awam</a> (<a href="search:عقيدة العوام">عقيدة العوام</a>) - <a href="search:Ahmad Al-Marzuqi">Syaikh Ahmad Al-Marzuqi</a></li>
        <li><a href="search:Al-Kharidah Al-Bahiyyah">Al-Kharidah Al-Bahiyyah</a> (<a href="search:الخريدة البهية">الخريدة البهية</a>) - <a href="search:Ahmad Ad-Dardir">Syaikh Ahmad Ad-Dardir</a></li>
    </ul>

    <h2 style="color: #0d6efd;">2. Bidang Fiqih & Ibadah</h2>
    <ul>
        <li><a href="search:Al-Muwaththa'">Al-Muwaththa'</a> (<a href="search:الموطأ">الموطأ</a>) - <a href="search:Imam Malik bin Anas">Imam Malik bin Anas</a></li>
        <li><a href="search:Al-Umm">Al-Umm</a> (<a href="search:الأم">الأم</a>) - <a href="search:Imam Muhammad bin Idris Asy-Syafi'i">Imam Muhammad bin Idris Asy-Syafi'i</a></li>
        <li><a href="search:Al-Mabsuth">Al-Mabsuth / Al-Ashl</a> (<a href="search:المبسوط">المبسوط / الأصل</a>) - <a href="search:Muhammad bin Al-Hasan Asy-Syaibani">Muhammad bin Al-Hasan Asy-Syaibani</a></li>
        <li><a href="search:Matan Abu Syuja'">Matan Abu Syuja' / Ghayatul Ikhtishar</a> (<a href="search:متن أبي شجاع">متن أبي شجاع</a>) - <a href="search:Al-Qadhi Abu Syuja'">Al-Qadhi Abu Syuja'</a></li>
        <li><a href="search:Minhajut Thalibin">Minhajut Thalibin</a> (<a href="search:منهاج الطالبين">منهاج الطالبين</a>) - <a href="search:Imam Yahya bin Syaraf An-Nawawi">Imam Yahya bin Syaraf An-Nawawi</a></li>
        <li><a href="search:Safinatun Najah">Safinatun Najah</a> (<a href="search:سفينة النجاة">سفينة النجاة</a>) - <a href="search:Salim bin Sumair Al-Hadhrami">Salim bin Sumair Al-Hadhrami</a></li>
        <li><a href="search:Qurratul 'Ain">Qurratul 'Ain bi Muhimmat Ad-Din</a> (<a href="search:قرة العين">قرة العين</a>) - <a href="search:Zainuddin Al-Malibari">Zainuddin Al-Malibari</a></li>
        <li><a href="search:Al-Hawi Al-Kabir">Al-Hawi Al-Kabir</a> (<a href="search:الحاوي الكبير">الحاوي الكبير</a>) - <a href="search:Imam Al-Mawardi">Imam Al-Mawardi</a></li>
        <li><a href="search:Bidayatul Hidayah">Bidayatul Hidayah</a> (<a href="search:بداية الهداية">بداية الهداية</a>) - <a href="search:Imam Abu Hamid Al-Ghazali">Imam Abu Hamid Al-Ghazali</a></li>
        <li><a href="search:Sullam At-Taufiq">Sullam At-Taufiq</a> (<a href="search:سلم التوفيق">سلم التوفيق</a>) - <a href="search:Abdullah bin Husain bin Thahir">Abdullah bin Husain bin Thahir</a></li>
        <li><a href="search:Al-Yaqut An-Nafis">Al-Yaqut An-Nafis</a> (<a href="search:الياقوت النفيس">الياقوت النفيس</a>) - <a href="search:Ahmad bin Umar Asy-Syathiri">Ahmad bin Umar Asy-Syathiri</a></li>
        <li><a href="search:Al-Majmu' Syarh Al-Muhadzdzab">Al-Majmu' Syarh Al-Muhadzdzab</a> (<a href="search:المجموع شرح المهذب">المجموع شرح المهذب</a>) - <a href="search:Imam Yahya bin Syaraf An-Nawawi">Imam Yahya bin Syaraf An-Nawawi</a></li>
        <li><a href="search:Bidayatul Mujtahid">Bidayatul Mujtahid</a> (<a href="search:بداية المجتهد">بداية المجتهد</a>) - <a href="search:Ibnu Rusyd Al-Hafid">Ibnu Rusyd Al-Hafid</a></li>
        <li><a href="search:Al-Mughni">Al-Mughni</a> (<a href="search:المغني">المغني</a>) - <a href="search:Ibnu Qudamah Al-Maqdisi">Ibnu Qudamah Al-Maqdisi</a></li>
        <li><a href="search:Nailul Authar">Nailul Authar</a> (<a href="search:نيل الأوطار">نيل الأوطار</a>) - <a href="search:Imam Asy-Syaukani">Imam Asy-Syaukani</a></li>
    </ul>

    <h2 style="color: #0d6efd;">3. Bidang Muamalah</h2>
    <ul>
        <li><a href="search:Al-Kharaj">Al-Kharaj</a> (<a href="search:الخراج">الخراج</a>) - <a href="search:Qadhi Abu Yusuf">Qadhi Abu Yusuf</a></li>
        <li><a href="search:Al-Amwal">Al-Amwal</a> (<a href="search:الأموال">الأموال</a>) - <a href="search:Abu Ubaid">Abu Ubaid Al-Qasim bin Salam</a></li>
        <li><a href="search:Al-Iktisab fi Ar-Rizq">Al-Iktisab fi Ar-Rizq</a> (<a href="search:الاكتساب">الاكتساب</a>) - <a href="search:Muhammad bin Al-Hasan Asy-Syaibani">Muhammad bin Al-Hasan Asy-Syaibani</a></li>
        <li><a href="search:Fathul Wahhab">Fathul Wahhab</a> (<a href="search:فتح الوهاب">فتح الوهاب</a>) - <a href="search:Syaikh Zakariyya Al-Anshari">Syaikh Zakariyya Al-Anshari</a></li>
        <li><a href="search:Bughyatul Mustarsyidin">Bughyatul Mustarsyidin</a> (<a href="search:بغية المسترشدين">بغية المسترشدين</a>) - <a href="search:Sayyid Abdurrahman Al-Masyhur">Sayyid Abdurrahman bin Muhammad Al-Masyhur</a></li>
        <li><a href="search:Ar-Rahabiyyah">Ar-Rahabiyyah</a> (<a href="search:الرحبية">الرحبية</a>) - <a href="search:Abu 'Abdillah Muhammad Ar-Rahabi">Abu 'Abdillah Muhammad Ar-Rahabi</a></li>
        <li><a href="search:Ahkam Al-Qur'an">Ahkam Al-Qur'an</a> (<a href="search:أحكام القرآن">أحكام القرآن</a>) - <a href="search:Al-Jasshash">Al-Jasshash</a></li>
    </ul>

    <h2 style="color: #0d6efd;">4. Bidang Al-Qur'an & Tafsir</h2>
    <ul>
        <li><a href="search:Tanwir Al-Miqbas">Tanwir Al-Miqbas min Tafsir Ibnu Abbas</a> (<a href="search:تنوير المقباس">تنوير المقباس</a>) - <a href="search:Abdullah bin Abbas">Abdullah bin Abbas</a></li>
        <li><a href="search:Tafsir Mujahid">Tafsir Mujahid</a> (<a href="search:تفسير مجاهد">تفسير مجاهد</a>) - <a href="search:Mujahid bin Jabr">Mujahid bin Jabr</a></li>
        <li><a href="search:Tafsir Ath-Thabari">Tafsir Ath-Thabari</a> (<a href="search:تفسير الطبري">تفسير الطبري</a>) - <a href="search:Imam Ibnu Jarir Ath-Thabari">Imam Ibnu Jarir Ath-Thabari</a></li>
        <li><a href="search:Ma'alim At-Tanzil">Ma'alim At-Tanzil / Tafsir Al-Baghawi</a> (<a href="search:معالم التنزيل">معالم التنزيل</a>) - <a href="search:Imam Al-Baghawi">Imam Al-Baghawi</a></li>
        <li><a href="search:Tafsir Ibnu Katsir">Tafsir Ibnu Katsir</a> (<a href="search:تفسير ابن كثير">تفسير ابن كثير</a>) - <a href="search:Imam Ibnu Katsir">Imam Ibnu Katsir</a></li>
        <li><a href="search:Tafsir Al-Qurthubi">Tafsir Al-Qurthubi</a> (<a href="search:تفسير القرطبي">تفسير القرطبي</a>) - <a href="search:Imam Al-Qurthubi">Imam Al-Qurthubi</a></li>
        <li><a href="search:Tafsir Al-Jalalain">Tafsir Al-Jalalain</a> (<a href="search:تفسير الجلالين">تفسير الجلالين</a>) - <a href="search:Jalaluddin As-Suyuthi">Jalaluddin As-Suyuthi</a></li>
        <li><a href="search:Al-Itqan fi 'Ulum Al-Qur'an">Al-Itqan fi 'Ulum Al-Qur'an</a> (<a href="search:الإتقان">الإتقان</a>) - <a href="search:Jalaluddin As-Suyuthi">Jalaluddin As-Suyuthi</a></li>
    </ul>

    <h2 style="color: #0d6efd;">5. Bidang Hadits & Ilmu Hadits</h2>
    <ul>
        <li><a href="search:Shahifah Hammam bin Munabbih">Shahifah Hammam bin Munabbih</a> (<a href="search:صحيفة همام">صحيفة همام</a>) - <a href="search:Abu Hurairah">Abu Hurairah</a></li>
        <li><a href="search:Musnad Ahmad bin Hanbal">Musnad Ahmad bin Hanbal</a> (<a href="search:مسند أحمد">مسند أحمد</a>) - <a href="search:Imam Ahmad bin Hanbal">Imam Ahmad bin Hanbal</a></li>
        <li><a href="search:Shahih Al-Bukhari">Shahih Al-Bukhari</a> (<a href="search:صحيح البخاري">صحيح البخاري</a>) - <a href="search:Imam Al-Bukhari">Imam Al-Bukhari</a></li>
        <li><a href="search:Shahih Muslim">Shahih Muslim</a> (<a href="search:صحيح مسلم">صحيح مسلم</a>) - <a href="search:Imam Muslim">Imam Muslim</a></li>
        <li><a href="search:Sunan Abu Dawud">Sunan Abu Dawud</a> (<a href="search:سنن أبي داود">سنن أبي داود</a>) - <a href="search:Imam Abu Dawud">Imam Abu Dawud</a></li>
        <li><a href="search:Sunan At-Tirmidzi">Sunan At-Tirmidzi</a> (<a href="search:سنن الترمذي">سنن الترمذي</a>) - <a href="search:Imam At-Tirmidzi">Imam At-Tirmidzi</a></li>
        <li><a href="search:Riyadhus Shalihin">Riyadhus Shalihin</a> (<a href="search:رياض الصالحين">رياض الصالحين</a>) - <a href="search:Imam An-Nawawi">Imam An-Nawawi</a></li>
        <li><a href="search:Bulughul Maram">Bulughul Maram</a> (<a href="search:بلوغ المرام">بلوغ المرام</a>) - <a href="search:Ibnu Hajar Al-Asqalani">Ibnu Hajar Al-Asqalani</a></li>
    </ul>

    <h2 style="color: #0d6efd;">6. Bidang Bahasa Arab</h2>
    <ul>
        <li><a href="search:Al-Kitab Sibawaih">Al-Kitab</a> (<a href="search:الكتاب">الكتاب</a>) - <a href="search:Sibawaih">Sibawaih</a></li>
        <li><a href="search:Al-Ajurrumiyyah">Al-Muqaddimah Al-Ajurrumiyyah</a> (<a href="search:الآجرومية">الآجرومية</a>) - <a href="search:Ibnu Ajurrum">Ibnu Ajurrum</a></li>
        <li><a href="search:Alfiyyah Ibnu Malik">Alfiyyah Ibnu Malik</a> (<a href="search:ألفية ابن مالك">ألفية ابن مالك</a>) - <a href="search:Imam Ibnu Malik">Imam Ibnu Malik</a></li>
        <li><a href="search:Nadhom Al-Imrithi">Nadhom Al-Imrithi</a> (<a href="search:العمريطي">العمريطي</a>) - <a href="search:Syarafuddin Al-Imrithi">Syarafuddin Al-Imrithi</a></li>
        <li><a href="search:Lisanul Arab">Lisanul Arab</a> (<a href="search:لسان العرب">لسان العرب</a>) - <a href="search:Ibnu Manzhur">Ibnu Manzhur</a></li>
    </ul>

    <h2 style="color: #0d6efd;">7. Bidang Sirah dan Sejarah</h2>
    <ul>
        <li><a href="search:Sirah Ibnu Ishaq">As-Sirah An-Nabawiyyah</a> (<a href="search:سيرة ابن إسحاق">سيرة ابن إسحاق</a>) - <a href="search:Ibnu Ishaq">Muhammad bin Ishaq</a></li>
        <li><a href="search:Sirah Nabawiyyah Ibnu Hisyam">Sirah Nabawiyyah Ibnu Hisyam</a> (<a href="search:سيرة ابن هشام">سيرة ابن هشام</a>) - <a href="search:Ibnu Hisyam">Abdul Malik bin Hisyam</a></li>
        <li><a href="search:Al-Bidayah wa An-Nihayah">Al-Bidayah wa An-Nihayah</a> (<a href="search:البداية والنهاية">البداية والنهاية</a>) - <a href="search:Imam Ibnu Katsir">Imam Ibnu Katsir</a></li>
        <li><a href="search:Asy-Syama'il Al-Muhammadiyyah">Asy-Syama'il Al-Muhammadiyyah</a> (<a href="search:الشمائل المحمدية">الشمائل المحمدية</a>) - <a href="search:Imam At-Tirmidzi">Imam At-Tirmidzi</a></li>
    </ul>

    <h2 style="color: #0d6efd;">8. Bidang Psikologi, Tasawuf, & Akhlaq</h2>
    <ul>
        <li><a href="search:Ihya' 'Ulumuddin">Ihya' 'Ulumuddin</a> (<a href="search:إحياء علوم الدين">إحياء علوم الدين</a>) - <a href="search:Imam Abu Hamid Al-Ghazali">Imam Abu Hamid Al-Ghazali</a></li>
        <li><a href="search:Al-Hikam">Al-Hikam</a> (<a href="search:الحكم العطائية">الحكم العطائية</a>) - <a href="search:Ibnu Atha'illah As-Sakandari">Ibnu Atha'illah As-Sakandari</a></li>
        <li><a href="search:Ta'limul Muta'allim">Ta'limul Muta'allim</a> (<a href="search:تعليم المتعلم">تعليم المتعلم</a>) - <a href="search:Az-Zarnuji">Syaikh Burhanuddin Az-Zarnuji</a></li>
        <li><a href="search:Nashaihul 'Ibad">Nashaihul 'Ibad</a> (<a href="search:نصائح العباد">نصائح العباد</a>) - <a href="search:Syaikh Nawawi Al-Bantani">Syaikh Nawawi Al-Bantani</a></li>
    </ul>

    <p style="text-align: center; margin-top: 50px; color: #999;">Cari Kitab - Dibuat dengan cinta untuk para pencari ilmu.</p>
</div>
"""
