COMPOSE=docker compose
CONTAINER=pai_ros2

.PHONY: help up down stop start restart rebuild pull logs ps shell root rm clean inspect

help:
	@echo ""
	@echo "ROS2 Docker Management"
	@echo ""
	@echo "  make up        : 起動（イメージ未取得時は自動pull）"
	@echo "  make down      : コンテナ削除"
	@echo "  make stop      : コンテナ停止"
	@echo "  make start     : コンテナ開始"
	@echo "  make restart   : コンテナ再起動"
	@echo "  make rebuild   : 最新イメージ取得後に再作成"
	@echo "  make pull      : 最新イメージ取得"
	@echo "  make logs      : ログ表示"
	@echo "  make ps        : 状態確認"
	@echo "  make shell     : bash接続"
	@echo "  make root      : rootで接続"
	@echo "  make inspect   : コンテナ情報表示"
	@echo "  make rm        : 同名コンテナ強制削除"
	@echo "  make clean     : コンテナ停止・削除＋不要イメージ削除"
	@echo ""

# 名前衝突回避
rm:
	-docker rm -f $(CONTAINER)

# 起動
up: rm
	UID=$$(id -u) $(COMPOSE) up -d --pull missing

# 停止
stop:
	$(COMPOSE) stop

# 開始
start:
	$(COMPOSE) start

# 再起動
restart:
	$(COMPOSE) restart

# 削除
down:
	$(COMPOSE) down

# 最新取得
pull:
	$(COMPOSE) pull

# 再作成
rebuild:
	$(COMPOSE) pull
	UID=$$(id -u) $(COMPOSE) up -d --force-recreate

# ログ
logs:
	$(COMPOSE) logs -f

# 状態
ps:
	$(COMPOSE) ps

# 通常接続
shell:
	$(COMPOSE) exec $(CONTAINER) bash

# root接続
root:
	$(COMPOSE) exec -u root $(CONTAINER) bash

# 詳細情報
inspect:
	docker inspect $(CONTAINER)

# クリーンアップ
clean:
	$(COMPOSE) down --remove-orphans
	docker image prune -f
	