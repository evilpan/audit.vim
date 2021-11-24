#!/bin/bash
DB_DIR="$HOME/audit.vim"
DB_INDEX="$DB_DIR/index"
FILE_EXTENSIONS=$(dirname $(realpath $0))/patterns.txt
FILE_LIST="audit.files"
CTAG_FILE=".tags"
SRC_DIR="."

log() {
    echo "[+] $@"
}

function create_flist() {
    local cmd="find $SRC_DIR -name LICENCES"
    for ext in `cat $FILE_EXTENSIONS`;do
        cmd="$cmd -o -name '$ext'"
    done
    log "collecting $FILE_LIST"
    eval $cmd > $FILE_LIST
    log "found `cat $FILE_LIST | wc -l` files"
}

function create_ctags() {

    log "creating ctags ..."
    ctags --fields=+l --links=no -f $CTAG_FILE -L $FILE_LIST
    log "ctags saved to $CTAG_FILE"
}

function create_cscope() {

    log "creating cscope db"
}

create_flist
create_ctags
create_cscope


function pz_audit() {
    local opt=$1
    local src=$PWD
    if [ ! -z $2 ];then
        src=`realpath $2`
    fi
    local idx_file="$HOME/.cscope.vim/index"
    local tag_file="$src/.tags"
    local marker_file="$src/.project"
    case "$opt" in
        add)
            if [ -e $tag_file ];then
                pz_log "tags file exists: $tag_file"
            else
                # http://ctags.sourceforge.net/ctags.html
                pz_log "generating $tag_file ..."
                ctags --fields=+l --links=no -f $tag_file -R $PWD
            fi
            if grep "$src|" $idx_file > /dev/null;then
                pz_log "cscope file exists: $src"
            else
                pz_log "generating cscope db ..."
                view -e "+:call CscopeFind('g', 'main')" "+:q"
            fi
            echo -n 1 > $marker_file
            pz_log "created $marker_file for AsyncRun.vim"
            ;;
        list)
            for m in `cat $idx_file`;do
                local _src=`echo $m | awk -F"|" '{print $1}'`
                local idx=`echo $m | awk -F"|" '{print $2}'`
                local _tags="$_src/.tags"
                local _csdb="$(dirname $idx_file)/$idx.db"
                local tg_size="N/A"
                local db_size="N/A"
                if [ -f $_tags ];then
                    tg_size=`ls -sh $_tags | awk '{print $1}'`
                fi
                if [ -f $_csdb ];then
                    db_size=`ls -sh $_csdb | awk '{print $1}'`
                fi
                printf "%-50s (tags:%+5s, cscope:%+5s)\n" "$_src" "$tg_size" "$db_size"
            done
            ;;
        rm)
            local bak=$idx_file.bak
            cp $idx_file $bak
            for m in `grep -n "$src|" $idx_file`;do
                local idx=`echo $m | awk -F"|" '{print $2}'`
                local lineno=`echo $m | awk -F: '{print $1}'`
                if [ -z "$idx" ];then
                    pz_log "cscope index not found, nothing to remove"
                    continue
                fi
                pz_log "cleaning ($lineno): $idx ..."
                sed -i.b "${lineno}d" $idx_file
                rm -vf $HOME/.cscope.vim/$idx.{db,files}
            done
            env diff $idx_file $bak
            rm -vf $tag_file
            rm -vf $marker_file
            ;;
        *)
            echo "Usage: pz_audit [add|rm|list] [src]"
            echo "vim leader is \`,'"
            echo ":AsyncRun -cwd=<root> rg -n passwd"
            echo ":cscope help"
            ;;
    esac
}
