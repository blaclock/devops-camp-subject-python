# 【課題】AWSセキュリティサービス

---

## 要件1: Webアプリケーションへの既知の攻撃を入口で防ぎたい

### 想定シナリオ
公開しているWebサービスに対して、SQLインジェクション・XSS・Log4j脆弱性を狙った攻撃など、既知のペイロードによる攻撃が届いている。アプリ側の対策に加えて、入口で広く・浅く防御する仕組みを入れたい。

### 選定サービス
- AWS WAF

### 選定理由
- AWSマネージドルール(AWS Managed Rules) を設定することで、広く・浅く防御するという要件を満たせる。
  - **根拠: AWS マネージドルールで SQLi・XSS・Log4j を防げること**

    出典: [Baseline rule groups - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-baseline.html)

    > 原文（英）: "The Known bad inputs rule group contains rules to block request patterns that are known to be invalid and are associated with exploitation or discovery of vulnerabilities. This can help reduce the risk of a malicious actor discovering a vulnerable application. ... Log4JRCE_HEADER — Inspects the keys and values of request headers for the presence of the Log4j vulnerability (CVE-2021-44228, CVE-2021-45046, CVE-2021-45105) and protects against Remote Code Execution (RCE) attempts. Example patterns include `${jndi:ldap://example.com/}`."
    >
    > 和訳: 「既知の不正な入力（Known bad inputs）ルールグループには、無効であることが既知でかつ脆弱性の悪用や探索に関連付けられたリクエストパターンをブロックするルールが含まれる。これにより悪意のある者が脆弱なアプリケーションを発見するリスクを軽減できる。... Log4JRCE_HEADER は、Log4j 脆弱性（CVE-2021-44228、CVE-2021-45046、CVE-2021-45105）の存在についてリクエストヘッダーのキーと値を検査し、リモートコード実行（RCE）の試みから保護する。例えば `${jndi:ldap://example.com/}` といったパターンが含まれる。」

    → この記述により「Known Bad Inputs ルールグループに Log4JRCE ルール（複数の CVE に対応）が含まれている」「AWS が運用・更新するルールセットで既知の脅威から防御できる」という選定理由が裏付けられる。

  - **根拠: SQLi・XSS 専用のマネージドルールが存在すること**

    出典: [Baseline rule groups - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-baseline.html)、および [Use-case specific rule groups - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-use-case.html)

    > 原文（英）: "The core rule set (CRS) rule group contains rules that are generally applicable to web applications. This provides protection against exploitation of a wide range of vulnerabilities, including some of the high risk and commonly occurring vulnerabilities described in OWASP publications such as OWASP Top 10. ... CrossSiteScripting_COOKIE — Inspects the values of cookie headers for common cross-site scripting (XSS) patterns using the built-in AWS WAF Cross-site scripting attack rule statement. ... The SQL database rule group contains rules to block request patterns associated with exploitation of SQL databases, like SQL injection attacks."
    >
    > 和訳: 「Core Rule Set (CRS) ルールグループには Web アプリケーション全般に適用可能なルールが含まれる。これは OWASP Top 10 など OWASP 出版物で説明されている高リスクで頻発する脆弱性を含む、広範な脆弱性の悪用に対する保護を提供する。... CrossSiteScripting_COOKIE は、組み込みの AWS WAF クロスサイトスクリプティング攻撃ルールステートメントを使用して一般的な XSS パターンについてクッキーヘッダーの値を検査する。... SQL database ルールグループには、SQL インジェクション攻撃のような SQL データベースの悪用に関連付けられたリクエストパターンをブロックするルールが含まれる。」

    → この記述により「CRS で XSS を含む OWASP Top 10 への対応」「SQL Database ルールグループで SQLi をブロック」という選定理由が裏付けられる。
- ALB や CloudFront、 API Gateway にアタッチすることで、アプリ側での対策に加えて入り口で防御できる。
  - **根拠: AWS WAF がAWSのリソースと連携して、 HTTP/HTTPS リクエストを L7 で検査できること**

    出典: [What is AWS WAF? - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html)

    > 原文（英）: "AWS WAF is a web application firewall that lets you monitor the HTTP and HTTPS requests that are forwarded to your protected web application resources. You can protect the following resource types: Amazon CloudFront distribution, Amazon API Gateway REST API, Application Load Balancer, AWS AppSync GraphQL API, Amazon Cognito user pool, AWS App Runner service, AWS Verified Access instance."
    >
    > 和訳: 「AWS WAF はウェブアプリケーションファイアウォールであり、保護対象の Web アプリケーションリソースに転送される HTTP および HTTPS リクエストを監視できる。次のリソースタイプを保護できる: Amazon CloudFront ディストリビューション、Amazon API Gateway REST API、Application Load Balancer、AWS AppSync GraphQL API、Amazon Cognito ユーザープール、AWS App Runner サービス、AWS Verified Access インスタンス。」

    → この記述により「AWS WAF は L7（HTTP/HTTPS）リクエストを検査できる」「CloudFront/ALB/API Gateway の前段に組み込める」という選定理由が裏付けられる。

### 代替案との比較
- AWS Network Firewall: VPC 内の L3/L4 トラフィック制御が主目的。HTTP リクエストの内容（SQLi/XSS パターン）検査には不向き。
- Security Groups / NACL: IP・ポート単位の制御は可能だが、ペイロード解析はできない。
- サードパーティ WAF（Cloudflare 等）: 機能的には可能だが、AWS リソース連携・IAM 統合・課金一元化の観点で AWS WAF が優位。

---

## 要件2: 大規模なDDoS攻撃からサービスを守りたい

### 想定シナリオ
公開サービスに対して、大量のトラフィックを送りつけてサービスを停止させる DDoS攻撃（L3/L4のボリューム攻撃、L7のHTTPフラッド）への対策を講じたい。

### 選定サービス
- AWS Shield Standard
- AWS Shield Advanced
- AWS WAF：L7 HTTP 
- Amazon CloudFront

### 選定理由
- AWS Shield Standard は L3/L4 のDDoS攻撃を自動的に緩和する。CloudFrontやRoute 53、ALB 等に標準で適用される。
  - **根拠: Shield Standard が L3/L4 ボリューム攻撃を自動緩和し、全 AWS ユーザに無償提供されること**

  出典: [AWS Shield Standard overview - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-standard-summary.html)

  > 原文（英）: "All AWS customers benefit from the automatic protection of Shield Standard, at no additional charge. Shield Standard defends against the most common, frequently occurring network and transport layer DDoS attacks that target your website or applications. While Shield Standard helps protect all AWS customers, you get particular benefit with Amazon Route 53 hosted zones, Amazon CloudFront distributions, and AWS Global Accelerator standard accelerators. These resources receive comprehensive availability protection against all known network and transport layer attacks."
  >
  > 和訳: 「すべての AWS ユーザは、追加料金なしで Shield Standard の自動保護の恩恵を受ける。Shield Standard は、ウェブサイトやアプリケーションを標的とする最も一般的で頻繁に発生するネットワーク層およびトランスポート層の DDoS 攻撃から防御する。Shield Standard はすべての AWS ユーザの保護を支援するが、Amazon Route 53 ホストゾーン、Amazon CloudFront ディストリビューション、AWS Global Accelerator スタンダードアクセラレーターでは特に恩恵を受けることができる。これらのリソースは、既知のすべてのネットワーク層およびトランスポート層攻撃に対する包括的な可用性保護を受ける。」

  → この記述により「Shield Standard が L3/L4 のネットワーク／トランスポート層の DDoS 攻撃を自動緩和」「全 AWS ユーザに自動適用・無償」「CloudFront/Route 53 等で特に効果」という選定理由が裏付けられる。

- AWS Shield Advanced は、SLA要件があるケースや、攻撃に対するより高いレベルの保護が必要な場合に使用する。
  - **根拠: Shield Advanced が詳細なリアルタイムメトリクスを提供すること**

    出典: [AWS Shield Advanced capabilities and options - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-advanced-summary-capabilities.html)
    
    > 原文（英）: "Enhanced visibility into DDoS events and attacks – Shield Advanced gives you access to advanced, real-time metrics and reports for extensive visibility into events and attacks on your protected AWS resources. You can access this information through the Shield Advanced API and console, and through Amazon CloudWatch metrics."
    >
    > 和訳: 「DDoS イベントおよび攻撃の可視性の強化 – Shield Advanced は、保護された AWS リソースに対するイベントや攻撃を広範に可視化するための、高度なリアルタイムメトリクスとレポートへのアクセスを提供する。この情報には Shield Advanced API・コンソール、および Amazon CloudWatch メトリクス経由でアクセスできる。」
    
- L7（HTTP フラッド）には AWS Shield では対応できないため、AWS WAF を使用する。
  - **根拠: AWS WAF レートベースルールで L7 HTTP フラッドを緩和できること**

    出典: [Using rate-based rule statements in AWS WAF - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html)
  
    > 原文（英）: "A rate-based rule counts incoming requests and rate limits requests when they are coming at too fast a rate. The rule aggregates requests according to your criteria, and counts and rate limits the aggregate groupings, based on the rule's evaluation window, request limit, and action settings."
    >
    > 和訳: 「レートベースルールは、流入リクエスト数をカウントし、リクエストが高頻度すぎる場合にレート制限を適用する。このルールは指定された条件でリクエストを集約し、ルールの評価ウィンドウ・リクエスト上限・アクション設定に基づき、その集約グループ単位でカウントおよびレート制限を行う。」

    → この記述により「WAF のレートベースルールで IP 単位のリクエスト数制限により L7 HTTP フラッドに対応」という選定理由が裏付けられる。
  
- CloudFront を設置することで、CloudFront の段階でブロックしてくれるので ALB などのオリジンへの到達を緩和する。
  - **根拠: CloudFront のグローバルエッジで Shield が DDoS 攻撃を吸収・緩和すること**

      出典: [AWS Shield mitigation logic for CloudFront and Route 53 - AWS WAF Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-event-mitigation-logic-continuous-inspection.html)
    
      > 原文（英）: "This page explains how Shield DDoS mitigation continually inspects traffic for CloudFront and Route 53. These services operate from a globally distributed network of AWS edge locations that provide you with broad access to Shield's DDoS mitigation capacity and deliver your application from infrastructure that's closer to your end users. ... CloudFront – Shield DDoS mitigations only allow traffic that's valid for web applications to pass through to the service. This provides automatic protection against many common DDoS vectors, like UDP reflection attacks. CloudFront maintains persistent connections to your application origin, TCP SYN floods are automatically mitigated through integration with the Shield TCP SYN proxy feature, and Transport Layer Security (TLS) is terminated at the edge. These combined features ensure that your application origin only receives well-formed web requests and that it's protected against lower-layer DDoS attacks, connection floods, and TLS abuse."
      >
      > 和訳: 「このページでは、CloudFront と Route 53 に対する Shield の DDoS 緩和が継続的にトラフィックを検査する仕組みを説明する。これらのサービスは AWS エッジロケーションのグローバル分散ネットワークから運用されており、Shield の DDoS 緩和キャパシティへの広範なアクセスを提供し、エンドユーザにより近いインフラストラクチャからアプリケーションを配信する。... CloudFront – Shield の DDoS 緩和は、Web アプリケーション向けに有効なトラフィックのみがサービスに通過することを許可する。これにより UDP リフレクション攻撃のような多くの一般的な DDoS ベクトルから自動的に保護される。CloudFront はアプリケーションオリジンへの永続接続を維持し、TCP SYN フラッドは Shield TCP SYN プロキシ機能との統合により自動的に緩和され、Transport Layer Security (TLS) はエッジで終端される。これらを組み合わせた機能により、アプリケーションオリジンは整形された Web リクエストのみを受信し、下位層の DDoS 攻撃、接続フラッド、TLS 悪用から保護される。」
    
    → この記述により「CloudFront をフロントに置くことで AWS のグローバルエッジが攻撃を吸収し、オリジン到達を抑制」「UDP リフレクション・TCP SYN フラッドなどの L3/L4 攻撃が自動緩和される」という選定理由が裏付けられる。


## 要件3: IAMの権限設計が適切か可視化したい

### 想定シナリオ
IAMユーザ・ロールに付与された権限が実際に必要な最小権限になっているか、外部に共有されるリソース（S3バケット・IAMロールなど）が意図せず公開されていないかをチェックしたい。

### 選定サービス
- IAM Access Analyzer

### 選定理由
- IAM Access Analyzer は、リソースベースポリシー（S3 バケット、IAM ロール、KMS キー、Lambda、SQS、Secrets Manager 等）を解析し、外部のアカウント・組織外への公開を自動検出する。
  - **根拠1: IAM Access Analyzer がリソースベースポリシーを論理推論で解析し外部公開を検出すること**

    出典: [Using AWS Identity and Access Management Access Analyzer - IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html) — 「Identifying resources shared with an external entity」セクション
    
    > 原文（英）: "IAM Access Analyzer helps you identify the resources in your organization and accounts, such as Amazon S3 buckets or IAM roles, shared with an external entity. This lets you identify unintended access to your resources and data, which is a security risk. IAM Access Analyzer identifies resources shared with external principals by using logic-based reasoning to analyze the resource-based policies in your AWS environment. For each instance of a resource shared outside of your account, IAM Access Analyzer generates a finding."
    >
    > 和訳: 「IAM Access Analyzer は、組織やアカウント内のリソース（Amazon S3 バケットや IAM ロールなど）で外部エンティティと共有されているものを特定するのに役立つ。これにより、セキュリティリスクとなる、リソースやデータへの意図しないアクセスを特定できる。IAM Access Analyzer は、論理ベースの推論（logic-based reasoning）を用いて AWS 環境内のリソースベースポリシーを解析することで、外部プリンシパルと共有されているリソースを特定する。アカウント外で共有されているリソースのインスタンスごとに、IAM Access Analyzer は検出結果（finding）を生成する。」
    
    → この記述により「リソースベースポリシー（S3 バケット、IAM ロール、KMS キー等）を解析して外部公開を自動検出」という選定理由が裏付けられる。

- さらに「未使用アクセスの検出」「最小権限ポリシー生成（CloudTrail から実利用状況を分析）」「ポリシーの検証」機能があり、最小権限設計の可視化に直接合致する。
  - **根拠: CloudTrail ログから最小権限ポリシーを生成できること**

    出典: [Using AWS Identity and Access Management Access Analyzer - IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html) — 「Generating policies」セクション    
    > 原文（英）: "IAM Access Analyzer analyzes your AWS CloudTrail logs to identify actions and services that have been used by an IAM entity (user or role) within your specified date range. It then generates an IAM policy that is based on that access activity. You can use the generated policy to refine an entity's permissions by attaching it to an IAM user or role."
    >
    > 和訳: 「IAM Access Analyzer は AWS CloudTrail ログを解析し、指定した日付範囲内で IAM エンティティ（ユーザまたはロール）が使用したアクションとサービスを特定する。次に、そのアクセスアクティビティに基づいた IAM ポリシーを生成する。生成されたポリシーを IAM ユーザまたはロールにアタッチすることで、エンティティの権限を絞り込むことができる。」    
    
    → この記述により「最小権限ポリシー生成（CloudTrail から実利用状況を分析）」という選定理由が裏付けられる。

  - **根拠: ポリシー検証機能（基本検証＋カスタムポリシーチェック）があること**

    出典: [Using AWS Identity and Access Management Access Analyzer - IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html) — 「Validating policies against AWS best practices」「Validating policies against your specified security standards」セクション
  
    > 原文（英）: "You can validate your policies against IAM policy grammar and AWS best practices using the basic policy checks provided by IAM Access Analyzer policy validation. ... You can validate your policies against your specified security standards using the IAM Access Analyzer custom policy checks. ... Through AWS CLI and AWS API, you can also check specific IAM actions that you consider critical are not allowed by a policy. These checks highlight a policy statement that grants new access."
    >
    > 和訳: 「IAM Access Analyzer のポリシー検証によって提供される基本ポリシーチェックを用いて、ポリシーを IAM ポリシー文法および AWS ベストプラクティスに対して検証できる。... IAM Access Analyzer のカスタムポリシーチェックを用いて、指定したセキュリティ標準に対してポリシーを検証できる。... AWS CLI および AWS API を通じて、重要だと考える特定の IAM アクションがポリシーで許可されていないかをチェックすることもできる。これらのチェックは、新たなアクセスを付与するポリシーステートメントを強調表示する。」
  
    → この記述により「ポリシーの検証」機能が IAM ベストプラクティス準拠＋カスタム標準準拠の両面で利用できることが裏付けられる。

---

## 要件4: 認証情報（DBパスワード・APIキー）を安全に管理したい

### 想定シナリオ
DB接続パスワード・サードパーティ APIキーなどの機密情報をコード内にハードコーディングせず、ローテーションやアクセス制御を行いたい。

### 選定サービス
- AWS Secrets Manager

### 選定理由
- Secrets Manager はIAM によるアクセス制御、自動ローテーションを実現できるため。
- アプリは AWS SDK 経由で機密情報を必要な時に取得するため、コード内ハードコーディングを排除できる。
  - **根拠: Secrets Manager がシークレットの管理・取得・ローテーションをライフサイクル全体で支援し、ハードコーディングを排除すること**

    出典: [What is AWS Secrets Manager? - AWS Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
  
    > 原文（英）: "AWS Secrets Manager helps you manage, retrieve, and rotate database credentials, application credentials, OAuth tokens, API keys, and other secrets throughout their lifecycles. Many AWS services store and use secrets in Secrets Manager. Secrets Manager helps you improve your security posture, because you no longer need hard-coded credentials in application source code. Storing the credentials in Secrets Manager helps avoid possible compromise by anyone who can inspect your application or the components. You replace hard-coded credentials with a runtime call to the Secrets Manager service to retrieve credentials dynamically when you need them."
    >
    > 和訳: 「AWS Secrets Manager は、データベース認証情報、アプリケーション認証情報、OAuth トークン、API キー、その他のシークレットを、ライフサイクル全体にわたり管理・取得・ローテーションすることを支援する。多くの AWS サービスがシークレットを Secrets Manager に保存・利用している。Secrets Manager によりアプリケーションソースコードにハードコーディングされた認証情報が不要になるため、セキュリティ態勢を改善できる。Secrets Manager に認証情報を保管することで、アプリケーションやそのコンポーネントを覗き見できる者による侵害の可能性を回避できる。ハードコーディングされた認証情報を、必要なときに動的に認証情報を取得する Secrets Manager サービスへのランタイムコールに置き換える。」
  
    → この記述により「DB パスワードや API キーをコード内ハードコーディングから排除」「アプリは AWS SDK 経由でランタイム取得」という選定理由が裏付けられる。
  - **根拠: IAM ベースの認証・アクセス制御に対応していること**

    出典: [Authentication and access control for AWS Secrets Manager - AWS Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access.html)
  
    > 原文（英）: "Secrets Manager uses AWS Identity and Access Management (IAM) to secure access to secrets. IAM provides authentication and access control. Authentication verifies the identity of individuals' requests. Secrets Manager uses a sign-in process with passwords, access keys, and multi-factor authentication (MFA) tokens to verify the identity of the users. ... Access control ensures that only approved individuals can perform operations on AWS resources such as secrets. Secrets Manager uses policies to define who has access to which resources, and which actions the identity can take on those resources. ... By using IAM permission policies, you control which users or services have access to your secrets. A permissions policy describes who can perform which actions on which resources."
    >
    > 和訳: 「Secrets Manager は、シークレットへのアクセスを保護するために AWS Identity and Access Management (IAM) を使用する。IAM は認証とアクセス制御を提供する。認証はリクエストを行う個人の身元を検証する。Secrets Manager は、パスワード、アクセスキー、多要素認証 (MFA) トークンによるサインインプロセスを使用してユーザの身元を検証する。... アクセス制御は、承認された個人のみがシークレットなどの AWS リソースに対して操作を実行できることを保証する。Secrets Manager はポリシーを使用して、誰がどのリソースにアクセスできるか、その ID がそれらのリソースに対してどのアクションを実行できるかを定義する。... IAM 権限ポリシーを使用することで、どのユーザやサービスがシークレットにアクセスできるかを制御する。権限ポリシーは、誰がどのリソースに対してどのアクションを実行できるかを記述する。」
  
    → この記述により「IAM ベースのアクセス制御」という選定理由が裏付けられる（Secrets Manager は IAM の認証＋ポリシー制御により、シークレット単位でアクセス許可を細粒度に管理できる）。



### 代替案との比較
- Parameter Store (SecureString): 自動ローテーション機能を持たず、今回の要件を満たすことができないため不採用。
  - **根拠: Parameter Store SecureString は KMS 暗号化に対応するが自動ローテーション非対応であること（代替案比較の根拠）**

    出典: [AWS Systems Manager Parameter Store - AWS Systems Manager User Guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
  
    > 原文（英）: "Parameter Store enables you to securely store, organize, and retrieve configuration simple configuration data at scale. It is designed to simplify configuration management across environments, allowing teams to standardize how applications access critical data without hardcoding values or relying on fragmented storage solutions. ... Parameter Store supports String, StringList, and SecureString parameter types. String and StringList parameter values are stored as plain text. SecureString parameters encrypt values using AWS Key Management Service, making them a practical choice for lightweight encrypted configuration values that don't require rotation or other advanced secret lifecycle capabilities. ... If you manage credentials that require automatic rotation, cross-account access, or fine-grained audit logging, we recommend using AWS Secrets Manager."
    >
    > 和訳: 「Parameter Store により、設定データを大規模にセキュアに保管・整理・取得できる。これは環境間の設定管理を簡素化するように設計されており、チームがアプリケーションから重要なデータにアクセスする方法を、値のハードコーディングや分散したストレージソリューションに依存せずに標準化できる。... Parameter Store は String、StringList、SecureString のパラメータタイプをサポートする。String および StringList のパラメータ値はプレーンテキストで保管される。SecureString パラメータは AWS Key Management Service を使用して値を暗号化し、ローテーションやその他の高度なシークレットライフサイクル機能を必要としない軽量の暗号化設定値の実用的な選択肢となる。... 自動ローテーション、クロスアカウントアクセス、または細粒度の監査ログを必要とする認証情報を管理する場合は、AWS Secrets Manager の使用を推奨する。」
  
    → この記述により「Parameter Store は KMS 暗号化と IAM 制御は可能だが、自動ローテーション機能を持たない」「機密情報は Secrets Manager、設定値は Parameter Store と使い分けるのがベストプラクティス」という選定理由・代替案比較が公式ドキュメントの推奨として明示的に裏付けられる。

---

## 要件5: データを保管時に暗号化し、暗号化鍵を一元管理したい

### 想定シナリオ
S3・RDS・EBSなどに保管するデータを 暗号化し、その暗号化鍵を一元管理・監査できる状態にしたい。

### 選定サービス
- AWS Key Management Service (KMS)

### 選定理由
- KMS は、各 AWS サービス（S3 / RDS / EBS / EFS / DynamoDB / Lambda 等）と統合済みのマネージド鍵管理サービス。CMK（カスタマー管理キー）でローテーション・キーポリシー・CloudTrail での利用ログによる監査が可能。
  - **根拠: KMS が AWS サービスと統合され、保管時／転送時暗号化に対応すること**

    出典: [Using AWS KMS encryption with AWS services - AWS Key Management Service Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/service-integration.html)
    
    > 原文（英）: "With AWS Key Management Service, you can provide encryption keys for protecting data in other AWS services. Using AWS KMS encryption with AWS services refers to the process of integrating AWS KMS with other AWS services to encrypt and decrypt data at rest or in transit. Developers, system administrators, and security professionals might be interested in this topic to secure sensitive data stored or transmitted through AWS services, meet regulatory compliance requirements, or implement encryption best practices. Common use cases include encrypting Amazon EBS volumes, Amazon S3 buckets, and Amazon RDS databases."
    >
    > 和訳: 「AWS Key Management Service を使用すれば、他の AWS サービス内のデータを保護するための暗号化キーを提供できる。AWS サービスでの AWS KMS 暗号化の使用とは、AWS KMS を他の AWS サービスと統合して、保管時または転送時のデータを暗号化・復号するプロセスを指す。開発者、システム管理者、セキュリティ専門家がこのトピックに関心を持つのは、AWS サービスを通じて保管または送信される機密データを保護するため、規制コンプライアンス要件を満たすため、または暗号化のベストプラクティスを実装するためである。一般的なユースケースには、Amazon EBS ボリューム、Amazon S3 バケット、Amazon RDS データベースの暗号化が含まれる。」
    
    → この記述により「S3 / RDS / EBS 等の AWS サービスと統合済み」「保管時の暗号化（Encryption at Rest）に対応」という選定理由が裏付けられる。
  - **根拠: KMS の自動キーローテーション機能があること**

     出典: [Rotate AWS KMS keys - AWS Key Management Service Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
     
     > 原文（英）: "To create new cryptographic material for your customer managed keys, you can create new KMS keys, and then change your applications or aliases to use the new KMS keys. Or, you can rotate the key material associated with an existing KMS key by enabling automatic key rotation or performing on-demand rotation. By default, when you enable automatic key rotation for a KMS key, AWS KMS generates new cryptographic material for the KMS key every year. You can also specify a custom rotation-period to define the number of days after you enable automatic key rotation that AWS KMS will rotate your key material, and the number of days between each automatic rotation thereafter."
     >
     > 和訳: 「カスタマー管理キー（CMK）に新しい暗号化マテリアルを作成するには、新しい KMS キーを作成してからアプリケーションやエイリアスを新しい KMS キーを使用するように変更する方法がある。あるいは、自動キーローテーションを有効化するかオンデマンドローテーションを実行することで、既存の KMS キーに関連付けられたキーマテリアルをローテーションできる。デフォルトでは、KMS キーに対して自動キーローテーションを有効化すると、AWS KMS は毎年新しい暗号化マテリアルを生成する。カスタムローテーション期間を指定して、自動キーローテーションを有効化してから AWS KMS がキーマテリアルをローテーションするまでの日数、およびそれ以降の各自動ローテーション間の日数を定義することもできる。」
     
     → この記述により「CMK でローテーションが可能」「カスタマー管理キー（CMK）でローテーション」という選定理由が裏付けられる。
- 「保管時の暗号化（Encryption at Rest）」と「鍵の一元管理・監査」という要件を満たす。
  - **根拠: KMS の操作が CloudTrail で監査ログとして記録されること**
    
    出典: [Logging AWS KMS API calls with AWS CloudTrail - AWS Key Management Service Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html)
    
    > 原文（英）: "AWS KMS is integrated with AWS CloudTrail, a service that records all calls to AWS KMS by users, roles, and other AWS services. CloudTrail captures all API calls to AWS KMS as events, including calls from the AWS KMS console, AWS KMS APIs, CloudFormation templates, the AWS Command Line Interface (AWS CLI), and AWS Tools for PowerShell. CloudTrail logs all AWS KMS operations, including read-only operations, ... operations that manage KMS keys, ... and cryptographic operations ..."
    >
    > 和訳: 「AWS KMS は AWS CloudTrail と統合されている。CloudTrail は、ユーザ、ロール、その他の AWS サービスによる AWS KMS へのすべての呼び出しを記録するサービスである。CloudTrail は AWS KMS コンソール、AWS KMS API、CloudFormation テンプレート、AWS コマンドラインインターフェイス (AWS CLI)、AWS Tools for PowerShell からの呼び出しを含む、AWS KMS のすべての API 呼び出しをイベントとしてキャプチャする。CloudTrail は、読み取り専用操作、... KMS キーを管理する操作、... 暗号化操作を含む、すべての AWS KMS 操作を記録する。」
    
    → この記述により「CloudTrail での利用ログによる監査が可能」という選定理由が裏付けられる。



### 代替案との比較
- CloudHSM: 専用 HSM が必要な厳格な規制（FIPS 140-2 Level 3）に対応する際に選択する。ただ、運用の負荷が高いため、各 AWS サービスとの統合は KMSのCKS(Customer Key Store)してCloudHSMを登録、関連付けすることで規制の要件を満たしつつ、運用の負荷を軽くすることができる。

---

## 要件6: 不審なアクティビティや潜在的な脅威を自動検知したい

### 想定シナリオ
クラウド環境全体で、異常なAPI呼び出し（例: 深夜に突然大量のIAMユーザ作成）、マルウェアに感染したEC2の挙動、既知の悪性IPとの通信などを自動検知したい。

### 選定サービス
- Amazon GuardDuty

### 選定理由
- GuardDuty は、CloudTrail 管理イベント / S3 データイベント / VPC フローログ / DNS ログ / EKS 監査ログ / Lambda ネットワークログなどを機械学習・脅威インテリジェンスで分析し、不審な挙動を自動検知する。
  - **根拠: GuardDuty が脅威インテリジェンスと機械学習で AWS データソースを継続監視・分析すること**  
    出典: [What is Amazon GuardDuty? - Amazon GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html)
    
    > 原文（英）: "Amazon GuardDuty is a threat detection service that continuously monitors, analyzes, and processes AWS data sources and logs in your AWS environment. GuardDuty uses threat intelligence feeds, such as lists of malicious IP addresses and domains, file hashes, and machine learning (ML) models to identify suspicious and potentially malicious activity in your AWS environment."
    >
    > 和訳: 「Amazon GuardDuty は脅威検出サービスであり、AWS 環境内の AWS データソースとログを継続的に監視・分析・処理する。GuardDuty は、悪意のある IP アドレスやドメインのリスト、ファイルハッシュなどの脅威インテリジェンスフィードと機械学習 (ML) モデルを使用して、AWS 環境内の疑わしいおよび潜在的に悪意のあるアクティビティを特定する。」
    
    → この記述により「機械学習・脅威インテリジェンスで分析」「不審な挙動を自動検知」という選定理由が裏付けられる。
    
  - **根拠: GuardDuty が CloudTrail 管理イベント / VPC フローログ / DNS ログを基本データソースとして取り込むこと**
    
    出典: [What is Amazon GuardDuty? - Amazon GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html) — 「Features of GuardDuty」セクション
    
    > 原文（英）: "Foundational threat detection – When you enable GuardDuty in an AWS account, GuardDuty automatically starts ingesting the foundational data sources associated with that account. These data sources include AWS CloudTrail management events, VPC flow logs (from Amazon EC2 instances), and DNS logs. You don't need to enable anything else for GuardDuty to start analyzing and processing these data sources to generate associated security findings."
    >
    > 和訳: 「基本脅威検出 — AWS アカウントで GuardDuty を有効化すると、GuardDuty はそのアカウントに関連付けられた基本データソースの取り込みを自動的に開始する。これらのデータソースには、AWS CloudTrail 管理イベント、VPC フローログ（Amazon EC2 インスタンスから）、DNS ログが含まれる。GuardDuty がこれらのデータソースを解析・処理してセキュリティ検出結果を生成するために、その他何も有効化する必要はない。」
    
    → この記述により「CloudTrail 管理イベント / VPC フローログ / DNS ログを分析」という選定理由が裏付けられる。
    
  - **根拠: GuardDuty が EKS 監査ログ・S3 データイベント・Lambda ネットワークログ等のユースケース別保護プランを提供すること**
    
    出典: [What is Amazon GuardDuty? - Amazon GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html) — 「Use-case focused GuardDuty protection plans」
    
    > 原文（英）: "Use-case focused GuardDuty protection plans – For enhanced threat detection visibility into the security of your AWS environment, GuardDuty offers dedicated protection plans that you can choose to enable. Protection plans help you monitor logs and events from other AWS services. These sources include EKS audit logs, RDS login activity, Amazon S3 data events in CloudTrail, EBS volumes, Runtime Monitoring across Amazon EKS, Amazon EC2, and Amazon ECS-Fargate, and Lambda network activity logs."
    >
    > 和訳: 「ユースケース別 GuardDuty 保護プラン — AWS 環境のセキュリティに対する脅威検出の可視性を強化するため、GuardDuty は有効化可能な専用の保護プランを提供する。保護プランは他の AWS サービスからのログとイベントの監視を支援する。これらのソースには、EKS 監査ログ、RDS ログインアクティビティ、CloudTrail 内の Amazon S3 データイベント、EBS ボリューム、Amazon EKS・Amazon EC2・Amazon ECS-Fargate にまたがるランタイムモニタリング、Lambda ネットワークアクティビティログが含まれる。」
    
    → この記述により「S3 データイベント / EKS 監査ログ / Lambda ネットワークログ」も保護プランで対応できることが裏付けられる。
- Malware Protection で EC2/EKS のマルウェア検知も可能。
  - **根拠: GuardDuty Malware Protection が EC2 にアタッチされた EBS ボリュームをスキャンしてマルウェア検知すること**

    出典: [GuardDuty Malware Protection for EC2 - Amazon GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection.html)
    
    > 原文（英）: "Malware Protection for EC2 helps you detect the potential presence of malware by scanning the Amazon Elastic Block Store (Amazon EBS) volumes that are attached to Amazon Elastic Compute Cloud (Amazon EC2) instances and container workloads running on Amazon EC2."
    >
    > 和訳: 「Malware Protection for EC2 は、Amazon EC2 上で実行されている Amazon Elastic Compute Cloud (Amazon EC2) インスタンスおよびコンテナワークロードにアタッチされた Amazon Elastic Block Store (Amazon EBS) ボリュームをスキャンすることで、マルウェアが存在する可能性を検出することを支援する。」
    
    → この記述により「Malware Protection で EC2 のマルウェア検知も可能」という選定理由が裏付けられる。

---

## 要件7: EC2・コンテナイメージの脆弱性をスキャンしたい

### 想定シナリオ
EC2インスタンスやコンテナイメージに含まれるOS・ミドルウェアのCVE脆弱性を自動で検出し、継続的にレポートが受け取れる状態にしたい。

### 選定サービス
- Amazon Inspector

### 選定理由
- Inspector は EC2 / ECR コンテナイメージ / Lambda 関数の脆弱性を継続的・自動にスキャンし、CVE をベースに検知する。
  - **根拠: Inspector が EC2 / ECR / Lambda を継続的に脆弱性スキャンすること**

    出典: [What is Amazon Inspector? - Amazon Inspector User Guide](https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html)
    
    > 原文（英）: "Amazon Inspector is a vulnerability management service that automatically discovers workloads and continually scans them for software vulnerabilities and unintended network exposure. Amazon Inspector discovers and scans Amazon EC2 instances, container images in Amazon ECR, and Lambda functions. When Amazon Inspector detects a software vulnerability or unintended network exposure, it creates a finding, which is a detailed report about the issue."
    >
    > 和訳: 「Amazon Inspector は脆弱性管理サービスであり、ワークロードを自動的に検出し、ソフトウェア脆弱性および意図しないネットワーク露出を継続的にスキャンする。Amazon Inspector は Amazon EC2 インスタンス、Amazon ECR 内のコンテナイメージ、Lambda 関数を検出してスキャンする。Amazon Inspector がソフトウェア脆弱性または意図しないネットワーク露出を検出すると、その問題に関する詳細レポートである検出結果（finding）を作成する。」
    
    → この記述により「コンテナイメージに含まれるOS・ミドルウェアのCVE脆弱性を自動で検出」という選定理由が裏付けられる。

  - **根拠: Inspector の検知結果が CVE データベースに基づき、CVSS 形式の重要度スコアで提示されること**

    出典: [What is Amazon Inspector? - Amazon Inspector User Guide](https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html) — 「Continuously scan your environment for vulnerabilities and network exposure」「Assess vulnerabilities accurately with the Amazon Inspector Risk score」セクション
    
    > 原文（英）: "Amazon Inspector continues to assess your environment throughout the lifecycle of your resources by automatically rescanning resources in response to changes that could introduce a new vulnerability, such as: installing a new package in an EC2 instance, installing a patch, and when a new common vulnerabilities and exposures (CVE) that impacts the resource is published. ... As Amazon Inspector collects information about your environment through scans, it provides severity scores specifically tailored to your environment. Amazon Inspector examines the security metrics that compose the National Vulnerability Database (NVD) base score for a vulnerability and adjusts them according to your compute environment. ... This score is in CVSS format and is a modification of the base Common Vulnerability Scoring System (CVSS) score provided by NVD."
    >
    > 和訳: 「Amazon Inspector は、新たな脆弱性をもたらす可能性のある変更（EC2 インスタンスへの新パッケージインストール、パッチ適用、リソースに影響を与える新規 CVE の公開など）に応じてリソースを自動的に再スキャンすることで、リソースのライフサイクル全体にわたり環境を継続的に評価する。... Amazon Inspector はスキャンを通じて環境に関する情報を収集する際、環境に特化した重要度スコアを提供する。Amazon Inspector は、脆弱性の National Vulnerability Database (NVD) ベーススコアを構成するセキュリティメトリクスを検査し、コンピューティング環境に応じて調整する。... このスコアは CVSS 形式であり、NVD が提供する Common Vulnerability Scoring System (CVSS) ベーススコアの修正版である。」
    
    → この記述により「CVE をベースに検知」「CVSS 形式の重要度スコアで提示」という選定理由が裏付けられる。

  - **根拠: ECR のコンテナイメージのプッシュ時／継続スキャンが可能であること**

    出典: [Scanning Amazon Elastic Container Registry container images with Amazon Inspector - Amazon Inspector User Guide](https://docs.aws.amazon.com/inspector/latest/user/scanning-ecr.html)
    
    > 原文（英）: "Amazon Inspector scans container images stored in Amazon Elastic Container Registry for software vulnerabilities to generate package vulnerability findings. When you activate Amazon ECR scanning, you set Amazon Inspector as the preferred scanning service for your private registry. ... With basic scanning, you can configure your repositories to scan on push or perform manual scans. With enhanced scanning, you scan for operating system and programming language package vulnerabilities at the registry level. ... Basic scanning is provided and billed through Amazon ECR. ... Enhanced scanning is provided and billed through Amazon Inspector."
    >
    > 和訳: 「Amazon Inspector は Amazon Elastic Container Registry に保管されたコンテナイメージのソフトウェア脆弱性をスキャンし、パッケージ脆弱性検出結果を生成する。Amazon ECR スキャンを有効化すると、プライベートレジストリの優先スキャンサービスとして Amazon Inspector が設定される。... 基本スキャンでは、リポジトリをプッシュ時スキャンに設定するか、手動スキャンを実行できる。拡張スキャンでは、レジストリレベルでオペレーティングシステムおよびプログラミング言語のパッケージ脆弱性をスキャンする。... 基本スキャンは Amazon ECR が提供・課金する。... 拡張スキャンは Amazon Inspector が提供・課金する。」
    
    → この記述により「ECR にプッシュされたイメージは自動スキャン」という選定理由が裏付けられる。

- 検出結果は Security Hub / EventBridge と連携でき、継続的なレポート要件に合致する。
  - **根拠: Security Hub CSPM / EventBridge との統合が可能であること**

    出典: [What is Amazon Inspector? - Amazon Inspector User Guide](https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html) — 「Monitor and process findings with other services and systems」セクション
    
    > 原文（英）: "To support integration with other services and systems, Amazon Inspector publishes findings to Amazon EventBridge as finding events. EventBridge is a serverless event bus service that can route findings data to targets such as AWS Lambda functions and Amazon Simple Notification Service (Amazon SNS) topics. With EventBridge, you can monitor and process findings in near-real time as part of your existing security and compliance workflows. If you have activated AWS Security Hub CSPM, then Amazon Inspector will also publish findings to Security Hub CSPM."
    >
    > 和訳: 「他のサービスやシステムとの統合をサポートするため、Amazon Inspector は検出結果イベントとして Amazon EventBridge に検出結果を発行する。EventBridge はサーバーレスイベントバスサービスであり、検出結果データを AWS Lambda 関数や Amazon Simple Notification Service (Amazon SNS) トピックなどのターゲットにルーティングできる。EventBridge を使用すれば、既存のセキュリティおよびコンプライアンスワークフローの一部として、検出結果をほぼリアルタイムで監視・処理できる。AWS Security Hub CSPM を有効化している場合、Amazon Inspector は検出結果を Security Hub CSPM にも発行する。」
    
    → この記述により「検出結果は Security Hub / EventBridge と連携でき、継続的なレポート要件に合致する」という選定理由が裏付けられる。

---

## 要件8: S3バケットの意図しない公開を防ぎたい

### 想定シナリオ
S3バケットが 誤ってパブリック公開 されないように、アカウント単位で公開をブロックしたい。また、既存バケットの公開状況を継続的にチェックしたい。

### 選定サービス
- S3 Block Public Access
- IAM Access Analyzer for S3
- AWS Config

### 選定理由
- S3 Block Public Access をアカウントレベルで有効化すれば、既存・新規バケットの意図しない公開を強制的にブロックできる。
  - **根拠: S3 Block Public Access がアカウント/バケット/アクセスポイント/Organizations レベルで公開を強制ブロックすること**

    出典: [Blocking public access to your Amazon S3 storage - Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
    
    > 原文（英）: "The Amazon S3 Block Public Access feature provides settings for access points, buckets, accounts, and AWS Organizations to help you manage public access to Amazon S3 resources. By default, new buckets, access points, and objects don't allow public access. However, users can modify bucket policies, access point policies, or object permissions to allow public access. S3 Block Public Access settings override these policies and permissions so that you can limit public access to these resources. With S3 Block Public Access, organization administrators, account administrators, and bucket owners can easily set up centralized controls to limit public access to their Amazon S3 resources that are enforced regardless of how the resources are created."
    >
    > 和訳: 「Amazon S3 Block Public Access 機能は、アクセスポイント、バケット、アカウント、AWS Organizations のための設定を提供し、Amazon S3 リソースへのパブリックアクセスの管理を支援する。デフォルトでは、新規のバケット、アクセスポイント、オブジェクトはパブリックアクセスを許可しない。しかし、ユーザはバケットポリシー、アクセスポイントポリシー、オブジェクト権限を変更してパブリックアクセスを許可することができる。S3 Block Public Access 設定はこれらのポリシーおよび権限を上書きし、これらのリソースへのパブリックアクセスを制限できるようにする。S3 Block Public Access により、組織管理者、アカウント管理者、バケット所有者は、リソースがどのように作成されたかに関係なく適用される、Amazon S3 リソースへのパブリックアクセスを制限する集中管理を簡単に設定できる。」
    
    → この記述により「Block Public Access をアカウントレベルで有効化すれば既存・新規バケットの意図しない公開を強制的にブロックできる」という選定理由が裏付けられる。

- IAM Access Analyzer for S3 は、ACL・バケットポリシー・アクセスポイントを継続的に解析し、外部公開・クロスアカウント共有を可視化する。
  - **根拠: IAM Access Analyzer for S3 が公開・クロスアカウント共有を可視化し、ACL・ポリシー・アクセスポイント別に共有元を示すこと**

    出典: [Reviewing bucket access using IAM Access Analyzer for S3 - Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-analyzer.html)
    
    > 原文（英）: "IAM Access Analyzer for S3 provides external access findings for your S3 general purpose buckets that are configured to allow access to anyone on the internet (public) or other AWS accounts, including AWS accounts outside of your organization. For each bucket that's shared publicly or with other AWS accounts, you receive findings into the source and level of shared access. For example, IAM Access Analyzer for S3 might show that a bucket has read or write access provided through a bucket access control list (ACL), a bucket policy, a Multi-Region Access Point policy, or an access point policy. With these findings, you can take immediate and precise corrective action to restore your bucket access to what you intended."
    >
    > 和訳: 「IAM Access Analyzer for S3 は、インターネット上の誰もにアクセスを許可している（パブリック）か、組織外の AWS アカウントを含む他の AWS アカウントにアクセスを許可するように設定された S3 汎用バケットに対する外部アクセス検出結果を提供する。パブリックまたは他の AWS アカウントと共有されている各バケットについて、共有アクセスのソースとレベルに関する検出結果を受け取る。例えば、IAM Access Analyzer for S3 は、バケットがバケットアクセスコントロールリスト (ACL)、バケットポリシー、Multi-Region Access Point ポリシー、またはアクセスポイントポリシーを通じて読み取りまたは書き込みアクセスを提供していることを示す場合がある。これらの検出結果により、意図したバケットアクセスを復元するための即時かつ精密な是正措置を取ることができる。」
    
    → この記述により「ACL・バケットポリシー・アクセスポイントを継続的に解析し、外部公開・クロスアカウント共有を可視化」という選定理由が裏付けられる。

- AWS Config ルールで公開状態を継続監視し、逸脱時に検知・自動修復（SSM Automation 等）が可能。
  - **根拠: AWS Config ルールで公開状態を継続評価できること**

    出典: [Evaluating Resources with AWS Config Rules - AWS Config Developer Guide](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config.html)
    
    > 原文（英）: "Use AWS Config to evaluate the configuration settings of your AWS resources. You do this by creating AWS Config rules, which represent your ideal configuration settings. AWS Config provides customizable, predefined rules called managed rules to help you get started."
    >
    > 和訳: 「AWS Config を使用して、AWS リソースの設定を評価する。これは、理想的な設定を表す AWS Config ルールを作成することで行う。AWS Config は、開始を支援するためのカスタマイズ可能で事前定義された「マネージドルール」を提供する。」
    
    → この記述により「AWS Config ルールで公開状態を継続監視できる」という選定理由が裏付けられる。マネージドルール `s3-bucket-public-read-prohibited` 等を使うことで S3 公開チェックを実装でき、逸脱時に検知・自動修復（SSM Automation 等）に連携できる。
    
---

## 要件9: 「誰が・いつ・何をしたか」の監査ログを保全したい

### 想定シナリオ
AWSアカウント内でのすべてのAPIコール（誰がどのリソースを操作したか）を記録し、改ざん防止された状態で長期保存したい。監査・インシデント調査に使えるログが必要。

### 選定サービス
- AWS CloudTrail
- Amazon S3
- AWS KMS

### 選定理由
- CloudTrail は AWS API コールを記録する。Organizations 配下で組織証跡を作れば、全アカウント・全リージョンの操作を一元的に保全できる。
  - **根拠1: CloudTrail が「誰が・いつ・何をしたか」を API イベントとして記録すること**

    出典: [What Is AWS CloudTrail? - AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)

    > 原文（英）: "AWS CloudTrail is an AWS service that helps you enable operational and risk auditing, governance, and compliance of your AWS account. Actions taken by a user, role, or an AWS service are recorded as events in CloudTrail. Events include actions taken in the AWS Management Console, AWS Command Line Interface, and AWS SDKs and APIs. ... Visibility into your AWS account activity is a key aspect of security and operational best practices. You can use CloudTrail to view, search, download, archive, analyze, and respond to account activity across your AWS infrastructure. You can identify who or what took which action, what resources were acted upon, when the event occurred, and other details to help you analyze and respond to activity in your AWS account."
    >
    > 和訳: 「AWS CloudTrail は、AWS アカウントの運用およびリスク監査、ガバナンス、コンプライアンスを有効化することを支援する AWS サービスである。ユーザ、ロール、または AWS サービスが実行したアクションは CloudTrail にイベントとして記録される。イベントには、AWS Management Console、AWS Command Line Interface、AWS SDK および API で実行されたアクションが含まれる。... AWS アカウントアクティビティの可視性は、セキュリティおよび運用ベストプラクティスの重要な側面である。CloudTrail を使用して、AWS インフラストラクチャ全体のアカウントアクティビティを表示・検索・ダウンロード・アーカイブ・分析・対応できる。誰または何がどのアクションを実行したか、どのリソースに対してアクションが行われたか、イベントがいつ発生したかなどの詳細を特定し、AWS アカウント内のアクティビティの分析と対応を支援できる。」

    → この記述により「CloudTrail は AWS API コールを記録する」「誰が・いつ・何をしたかを記録できる」という選定理由が裏付けられる。

  - **根拠2: Organizations 配下で組織証跡として全アカウントのイベントを記録できること**

    出典: [Creating a trail for an organization - AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html)

    > 原文（英）: "If you have created an organization in AWS Organizations, you can create a trail that logs all events for all AWS accounts in that organization. This is sometimes called an organization trail. ... All organization trails created using the console are multi-Region organization trails that log events from the enabled AWS Regions in each member account in the organization. ... Users with CloudTrail permissions in member accounts can see organization trails when they log into the CloudTrail console from their AWS accounts, or when they run AWS CLI commands such as describe-trails. However, users in member accounts do not have sufficient permissions to delete organization trails, turn logging on or off, change what types of events are logged, or otherwise change an organization trail in any way."
    >
    > 和訳: 「AWS Organizations で組織を作成している場合、その組織内のすべての AWS アカウントのすべてのイベントを記録する証跡を作成できる。これは「組織証跡 (organization trail)」と呼ばれることがある。... コンソールから作成されるすべての組織証跡はマルチリージョン組織証跡であり、組織内の各メンバーアカウントで有効化された AWS リージョンからイベントを記録する。... メンバーアカウントの CloudTrail 権限を持つユーザは、AWS アカウントから CloudTrail コンソールにログインしたとき、または describe-trails などの AWS CLI コマンドを実行したときに組織証跡を見ることができる。ただし、メンバーアカウントのユーザは、組織証跡を削除する、ログ記録のオン/オフを切り替える、記録されるイベントタイプを変更する、その他のいかなる方法でも組織証跡を変更するための十分な権限を持たない。」

    → この記述により「Organizations 配下で組織証跡を作れば全アカウント・全リージョンの操作を一元的に保全」「メンバーアカウントから改ざんできない」という選定理由が裏付けられる。

- 改ざん防止には:
  - CloudTrail のログファイル整合性検証（Log File Validation） で SHA-256 ハッシュ署名を有効化
    - **根拠: CloudTrail ログファイル整合性検証（Log File Validation）が SHA-256 と RSA で改ざんを検知すること**

      出典: [Validating CloudTrail log file integrity - AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html)

      > 原文（英）: "To determine whether a log file was modified, deleted, or unchanged after CloudTrail delivered it, you can use CloudTrail log file integrity validation. This feature is built using industry standard algorithms: SHA-256 for hashing and SHA-256 with RSA for digital signing. This makes it computationally infeasible to modify, delete or forge CloudTrail log files without detection. ... When you enable log file integrity validation, CloudTrail creates a hash for every log file that it delivers. Every hour, CloudTrail also creates and delivers a file that references the log files for the last hour and contains a hash of each. This file is called a digest file. CloudTrail signs each digest file using the private key of a public and private key pair."
      >
      > 和訳: 「CloudTrail によって配信された後にログファイルが変更、削除、または変更されていないかを判定するために、CloudTrail のログファイル整合性検証を使用できる。この機能は業界標準のアルゴリズム（ハッシュ化に SHA-256、デジタル署名に SHA-256 with RSA）を用いて構築されている。これにより、検出なしに CloudTrail ログファイルを変更、削除、または偽造することは計算上不可能になる。... ログファイル整合性検証を有効化すると、CloudTrail は配信するすべてのログファイルに対してハッシュを作成する。CloudTrail は 1 時間ごとに、過去 1 時間のログファイルを参照し各ハッシュを含むファイルも作成・配信する。このファイルは「ダイジェストファイル」と呼ばれる。CloudTrail は公開鍵・秘密鍵ペアの秘密鍵を使用して各ダイジェストファイルに署名する。」

      → この記述により「ログファイル整合性検証で SHA-256 ハッシュ署名を有効化することで改ざん検知できる」という選定理由が裏付けられる。

  - 保存先 S3 バケットに S3 Object Lock（コンプライアンスモード） + バージョニングを設定し、削除・上書きを物理的に阻止
    - **根拠: S3 Object Lock が WORM モデルでログ削除・上書きを物理的に阻止すること**

      出典: [Locking objects with Object Lock - Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)

      > 原文（英）: "S3 Object Lock can help prevent Amazon S3 objects from being deleted or overwritten for a fixed amount of time or indefinitely. Object Lock uses a write-once-read-many (WORM) model to store objects. You can use Object Lock to help meet regulatory requirements that require WORM storage, or to add another layer of protection against object changes or deletion. ... In compliance mode, a protected object version can't be overwritten or deleted by any user, including the root user in your AWS account. When an object is locked in compliance mode, its retention mode can't be changed, and its retention period can't be shortened. Compliance mode helps ensure that an object version can't be overwritten or deleted for the duration of the retention period."
      >
      > 和訳: 「S3 Object Lock は、固定期間または無期限に Amazon S3 オブジェクトの削除や上書きを防止することを支援できる。Object Lock は Write-Once-Read-Many (WORM) モデルを使用してオブジェクトを保管する。Object Lock を使用して WORM ストレージを必要とする規制要件を満たすことや、オブジェクトの変更や削除に対する追加の保護層を加えることができる。... コンプライアンスモードでは、保護されたオブジェクトのバージョンは AWS アカウントのルートユーザを含むいかなるユーザも上書きや削除ができない。オブジェクトがコンプライアンスモードでロックされた場合、その保持モードを変更することはできず、保持期間を短縮することもできない。コンプライアンスモードは、保持期間中、オブジェクトのバージョンが上書き・削除されないことを確実に保証することを支援する。」

      → この記述により「S3 Object Lock（コンプライアンスモード）+ バージョニングで削除・上書きを物理的に阻止」という選定理由が裏付けられる。

  - SSE-KMS で暗号化、KMS キーポリシーで削除権限を分離（IAM 職務分掌）
    - **根拠: CloudTrail ログを SSE-KMS で暗号化できること**

      出典: [Encrypting CloudTrail log files, digest files, and event data stores with AWS KMS keys (SSE-KMS) - AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/encrypting-cloudtrail-log-files-with-aws-kms.html)

      > 原文（英）: "By default, the log files and digest files delivered by CloudTrail to your bucket are encrypted by using server-side encryption with a KMS key (SSE-KMS). If you don't enable SSE-KMS encryption, your log files and digest files are encrypted using SSE-S3 encryption. ... To use SSE-KMS with CloudTrail, you create and manage a AWS KMS key. You attach a policy to the key that determines which users can use the key for encrypting and decrypting CloudTrail log files and digest files."
      >
      > 和訳: 「デフォルトでは、CloudTrail によってバケットに配信されるログファイルおよびダイジェストファイルは、KMS キーを使用したサーバー側暗号化 (SSE-KMS) で暗号化される。SSE-KMS 暗号化を有効化しない場合、ログファイルおよびダイジェストファイルは SSE-S3 暗号化で暗号化される。... CloudTrail で SSE-KMS を使用するには、AWS KMS キーを作成・管理する。キーにポリシーをアタッチすることで、どのユーザが CloudTrail ログファイルおよびダイジェストファイルの暗号化・復号にキーを使用できるかを決定する。」

      → この記述により「SSE-KMS で暗号化、KMS キーポリシーで削除権限を分離（IAM 職務分掌）」という選定理由が裏付けられる。

- ライフサイクルポリシーで Glacier に移行することで長期保存コストを抑えられる。
  - **根拠: S3 ライフサイクルポリシーで Glacier 等の長期保存階層への移行ができること**

    出典: [Managing the lifecycle of objects - Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)

    > 原文（英）: "S3 Lifecycle helps you store objects cost effectively throughout their lifecycle by transitioning them to lower-cost storage classes, or, deleting expired objects on your behalf. To manage the lifecycle of your objects, create an S3 Lifecycle configuration for your bucket. An S3 Lifecycle configuration is a set of rules that define actions that Amazon S3 applies to a group of objects. There are two types of actions: Transition actions – These actions define when objects transition to another storage class. For example, you might choose to transition objects to the S3 Standard-IA storage class 30 days after creating them, or archive objects to the S3 Glacier Flexible Retrieval storage class one year after creating them."
    >
    > 和訳: 「S3 ライフサイクルは、オブジェクトを低コストのストレージクラスに移行する、または期限切れオブジェクトを代わりに削除することで、オブジェクトをライフサイクル全体でコスト効率よく保管することを支援する。オブジェクトのライフサイクルを管理するには、バケットに S3 ライフサイクル設定を作成する。S3 ライフサイクル設定は、Amazon S3 がオブジェクトのグループに適用するアクションを定義するルールセットである。アクションには 2 種類ある: 移行アクション — これらのアクションは、オブジェクトが別のストレージクラスに移行するタイミングを定義する。例えば、オブジェクト作成から 30 日後に S3 Standard-IA ストレージクラスに移行する、または 1 年後に S3 Glacier Flexible Retrieval ストレージクラスにアーカイブする、といった選択ができる。」

    → この記述により「ライフサイクルポリシーで Glacier に移行することで長期保存コストを抑えられる」という選定理由が裏付けられる。

---
